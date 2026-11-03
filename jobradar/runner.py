"""Run engine: units = (source, role keyword). Honest outcome: succeeded / partial (names) / blocked (reason) / cancelled.
Resume continues the latest unfinished run: done units are skipped, blocked units are retried, rows are keyed so nothing duplicates."""
import json
from . import store, collectors as C


def role_terms(p):
    return [r.strip() for r in p["target_roles"] if r.strip()]


def latest_unfinished(c):
    return c.execute("select * from runs where status in ('running','cancelled') order by id desc limit 1").fetchone()


def summarize(c, run_id, sources, terms):
    per, ok, bad = {}, [], []
    for s in sources:
        u = c.execute("select unit,status,reason,rows from run_units where run_id=? and source=?", (run_id, s)).fetchall()
        done = [x for x in u if x["status"] == "done"]
        blocked = [x for x in u if x["status"] == "blocked"]
        rows = sum(x["rows"] or 0 for x in done)
        reasons = sorted({x["reason"] for x in blocked})
        if len(done) == len(terms):
            st = "ok"
        elif done:
            st = "partial"
        else:
            st = "blocked"
        per[s] = {"name": C.NAMES[s], "status": st, "units_done": len(done), "units_total": len(terms), "rows": rows, "reasons": reasons,
                  "zero_rows": st == "ok" and rows == 0}
        (ok if st == "ok" else bad).append(s)
    if not bad:
        outcome = "succeeded"
    elif any(v["status"] in ("ok", "partial") for v in per.values()):
        outcome = "partial"
    else:
        outcome = "blocked"
    return outcome, per


def message(outcome, per):
    if outcome == "succeeded":
        z = [v["name"] for v in per.values() if v["zero_rows"]]
        return "succeeded" + (f" (but {', '.join(z)} returned 0 jobs for your roles; that is a real empty result, not an error)" if z else "")
    bad = [f'{v["name"]}: {"; ".join(v["reasons"]) or "incomplete"}' for v in per.values() if v["status"] != "ok"]
    return f"{outcome}: " + " | ".join(bad)


def run(ws, p, http, sources=None, resume=False, stop_after_units=None, pages=1, details=8, log=print):
    c = store.conn(ws)
    sources = list(sources or C.UNITS)
    for s in sources:
        if s in C.DISABLED:
            raise ValueError(f"{s} is {C.DISABLED[s]}")
        if s not in C.UNITS:
            raise ValueError(f"unknown source {s}; choose from {', '.join(C.UNITS)}")
    terms = role_terms(p)
    prev = latest_unfinished(c) if resume else None
    if prev:
        run_id = prev["id"]
        c.execute("update runs set status='running' where id=?", (run_id,))
        log(f"resuming run {run_id}")
    else:
        run_id = c.execute("insert into runs(started,status,summary) values(?,?,?)", (store.now(), "running", "{}")).lastrowid
    c.commit()
    done = {(r["source"], r["unit"]) for r in c.execute("select source,unit from run_units where run_id=? and status='done'", (run_id,))}
    stopped, blocked_now, processed = False, set(), 0
    try:
        for s in sources:
            for t in terms:
                if (s, t) in done or s in blocked_now:
                    continue
                if stop_after_units is not None and processed >= stop_after_units:
                    stopped = True
                    break
                try:
                    rows = C.UNITS[s](http, t, pages=pages, details=details, known=store.known_keys(c))
                    store.upsert(c, rows, run_id)
                    seen = getattr(rows, "seen", 0)
                    c.execute("insert or replace into run_units values(?,?,?,?,?,?,?)", (run_id, s, t, "done", "", len(rows) + seen, store.now()))
                    log(f"  {C.NAMES[s]} / {t}: {len(rows) + seen} jobs" + (f" ({seen} already stored, not re-read)" if seen else ""))
                except C.Blocked as e:
                    c.execute("insert or replace into run_units values(?,?,?,?,?,?,?)", (run_id, s, t, "blocked", e.reason, 0, store.now()))
                    blocked_now.add(s)
                    log(f"  {C.NAMES[s]} / {t}: BLOCKED {e.reason}")
                c.commit()
                processed += 1
            if stopped:
                break
    except KeyboardInterrupt:
        stopped = True
    if stopped:
        c.execute("update runs set status='cancelled', finished=? where id=?", (store.now(), run_id))
        c.commit()
        return {"run_id": run_id, "outcome": "cancelled", "message": "cancelled; continue with: python -m jobradar run --resume", "sources": {}}
    outcome, per = summarize(c, run_id, sources, terms)
    msg = message(outcome, per)
    c.execute("update runs set status=?, finished=?, summary=? where id=?",
              (outcome, store.now(), json.dumps({"message": msg, "sources": per}, ensure_ascii=False), run_id))
    c.commit()
    return {"run_id": run_id, "outcome": outcome, "message": msg, "sources": per}


def coverage(ws):
    """Coverage disclosure for the report: per source attempted / succeeded / blocked / last success, from the latest finished run."""
    c = store.conn(ws)
    run_row = c.execute("select * from runs where status in ('succeeded','partial','blocked') order by id desc limit 1").fetchone()
    cov = []
    for s, name in C.NAMES.items():
        last = c.execute("select max(ts) from run_units where source=? and status='done'", (s,)).fetchone()[0]
        # each source reports its own latest finished run, so a one-source re-run does not zero the others
        src_run = c.execute("""select r.id from runs r join run_units u on u.run_id=r.id where u.source=?
                               and r.status in ('succeeded','partial','blocked') order by r.id desc limit 1""", (s,)).fetchone()
        u = c.execute("select status,reason,rows from run_units where run_id=? and source=?", (src_run[0], s)).fetchall() if src_run else []
        cov.append({"source": name, "attempted": len(u), "succeeded": sum(1 for x in u if x["status"] == "done"),
                    "blocked": sorted({x["reason"] for x in u if x["status"] == "blocked"}), "rows": sum(x["rows"] or 0 for x in u),
                    "last_success": last or "never", "disabled": False})
    for s, why in C.DISABLED.items():
        cov.append({"source": s.capitalize(), "attempted": 0, "succeeded": 0, "blocked": [why], "rows": 0, "last_success": "never", "disabled": True})
    return run_row, cov
