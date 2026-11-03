"""Offline HTML report + workspace page (save / hide / note), CSV/JSON export, and the tiny local server.
Interface language follows profile.ui_lang: fa (Persian, right-to-left, default) or en. Job text is shown as published."""
import html, json, csv, io, pathlib, datetime as dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import store, rank as R, runner, profile as P, i18n, links, updater

E = html.escape


def ranked(ws):
    c = store.conn(ws)
    p = P.load(ws)
    st = store.states(c)
    rows = R.rank(p, [dict(r, key=r["key"]) for r in store.all_obs(c)])
    for r in rows:
        s = st.get(r["key"], {})
        r["state"], r["note"] = s.get("state", "none"), s.get("note", "")
    return p, rows


MODE = {"fa": {"remote": "دورکاری", "hybrid": "ترکیبی", "onsite": "حضوری"}, "en": {}}


def card(r, interactive, lang):
    L = i18n.t(lang)
    k = E(r["key"], quote=True)
    also = "".join(f' <a href="{E(a["url"], quote=True)}">{E(a["source"])}</a>' for a in r["also_on"])
    btn = ""
    if interactive:
        btn = (f'<div class="act"><button onclick="setState(\'{k}\',\'saved\')">{L["save"]}</button> '
               f'<button onclick="setState(\'{k}\',\'hidden\')">{L["hide"]}</button> '
               f'<button onclick="setState(\'{k}\',\'none\')">{L["clear"]}</button></div>'
               f'<textarea dir="auto" placeholder="{E(L["note_ph"], quote=True)}" onblur="setNote(\'{k}\',this.value)">{E(r["note"])}</textarea>')
    elif r["note"]:
        btn = f'<p dir="auto"><b>{L["note"]}:</b> {E(r["note"])}</p>'
    mode = MODE.get(lang, {}).get(r["work_mode"], r["work_mode"])
    meta = " · ".join(f'<bdi>{E(x)}</bdi>' for x in (r["company"], r["location"], mode, i18n.emp(lang, r["employment"]), r["salary"], r["posted_at"]) if x and x != "unknown")
    why = r["why_fa"] if lang == "fa" else r["why"]
    return (f'<article class="card {E(r["state"])}"><h3><a dir="auto" href="{E(r["url"], quote=True)}">{E(r["title"])}</a> '
            f'<span class="score" title="{L["why_head"]}">{i18n.num(lang, r["score"])}</span></h3>'
            f'<p class="meta">{meta} · <bdi>{E(r["source"])}</bdi>{(" · " + L["also_on"] + also) if also else ""}</p>'
            f'<details class="why"><summary>{L["why_head"]}</summary><ul>{"".join(f"<li><bdi>{E(w)}</bdi></li>" for w in why)}</ul></details>{btn}</article>')


JS = """<script>
const FAIL=%s;
async function post(b){const r=await fetch('/api/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});if(!r.ok)alert(FAIL);return r.ok}
async function setState(k,s){if(await post({key:k,state:s}))location.reload()}
async function setNote(k,n){await post({key:k,note:n})}
</script>"""

CSS = """@font-face{font-family:Vazirmatn;src:local('Vazirmatn'),url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn[wght].woff2') format('woff2');font-weight:100 900;font-display:swap}
:root{--fg:#1d1d1f;--mut:#5f6368;--bd:#dadce0;--ok:#1e8e3e;--okbg:#eef8f0;--bad:#b3261e;--chip:#f1f3f4;--bg:#fff}
@media(prefers-color-scheme:dark){:root{--fg:#e8eaed;--mut:#9aa0a6;--bd:#3c4043;--ok:#81c995;--okbg:#1b2a1f;--bad:#f28b82;--chip:#303134;--bg:#202124}}
body{font:15px/1.7 Vazirmatn,Tahoma,system-ui,sans-serif;max-width:920px;margin:2em auto;padding:0 1em;color:var(--fg);background:var(--bg)}
a{color:inherit}h1{margin-bottom:.2em}h2{margin-top:1.6em;border-bottom:1px solid var(--bd);padding-bottom:.2em}
.card{border:1px solid var(--bd);border-radius:10px;padding:.6em 1em;margin:.8em 0}.card.saved{border-color:var(--ok);background:var(--okbg)}
.card h3{margin:.2em 0;font-size:1.05em}.card h3 a{text-decoration:none}.card h3 a:hover{text-decoration:underline;text-underline-offset:.35em}.score{background:var(--chip);border-radius:6px;padding:0 .45em;font-size:.8em;font-weight:400}
.meta{color:var(--mut);margin:.2em 0;font-size:.92em}.why{color:var(--mut);font-size:.9em}.why ul{margin:.3em 0}
table{border-collapse:collapse;width:100%;font-size:.93em}td,th{border:1px solid var(--bd);padding:.35em .55em;text-align:start}.blocked{color:var(--bad)}
textarea{width:100%;min-height:2.4em;font:inherit;box-sizing:border-box;margin-top:.3em}button{font:inherit;padding:.15em .8em;border-radius:6px;border:1px solid var(--bd);background:var(--chip);color:inherit;cursor:pointer}
code{direction:ltr;unicode-bidi:isolate;background:var(--chip);padding:0 .3em;border-radius:4px}.lnk a{display:inline-block;margin:.15em .35em .15em 0}
.banner{border-inline-start:4px solid var(--ok);padding:.4em .8em;background:var(--chip);border-radius:6px}.banner.partial,.banner.blocked{border-color:var(--bad)}
.tip{color:var(--mut);font-size:.9em}"""


def _manual(p, lang):
    L = i18n.t(lang)
    rows = ""
    for m in links.manual_links(p):
        name = m["fa"] if lang == "fa" else m["en"]
        a = "".join(f'<a dir="auto" href="{E(s["url"], quote=True)}" target="_blank" rel="noopener">{E(s["role"])}</a>' for s in m["searches"])
        rows += f"<tr><td>{E(name)}</td><td class='lnk'>{a}</td></tr>"
    return f'<h2>{L["manual"]}</h2><p class="tip">{L["manual_why"]}</p><table>{rows}</table>'


def _companies(lang):
    L = i18n.t(lang)
    try:
        cs = links.companies()
    except Exception:
        return ""
    items = "".join(f'<a href="{E(c["url"], quote=True)}" target="_blank" rel="noopener">{E(c["name_fa"] if lang == "fa" else c["name"])}</a>' for c in cs)
    return f'<h2>{L["companies"]}</h2><p class="tip">{L["companies_why"]}</p><p class="lnk">{items}</p>'


def render(ws, interactive=False, limit=100):
    p, rows = ranked(ws)
    lang = p.get("ui_lang") if p.get("ui_lang") in ("fa", "en") else "fa"
    L = i18n.t(lang)
    run_row, cov = runner.coverage(ws)
    visible = [r for r in rows if r["state"] != "hidden" and not (r.get("excluded") and r["state"] != "saved")]
    hidden = [r for r in rows if r["state"] == "hidden" or (r.get("excluded") and r["state"] != "saved")]
    saved = [r for r in visible if r["state"] == "saved"]
    rest = [r for r in visible if r["state"] != "saved" and r["matched"]][:limit]
    unmatched = sum(1 for r in visible if not r["matched"] and r["state"] != "saved")

    up = updater.check_update(ws, force=False, timeout=1.0)
    up_banner = ""
    if up and up.get("has_update"):
        msg = up["message_fa"] if lang == "fa" else up["message_en"]
        up_banner = f'<div class="banner" style="border-inline-start-color:var(--ok);margin-bottom:1em">💡 <b>{E(L["update_available"])}:</b> {E(msg)} <a href="{E(up["url"])}" target="_blank" rel="noopener">GitHub</a></div>'

    if run_row:
        summ = json.loads(run_row["summary"] or "{}")
        st = run_row["status"]
        msg = summ.get("message", "")
        if msg.strip() == st:
            msg = ""
        if lang == "fa":
            msg = " | ".join(i18n.reason("fa", x) for x in msg.split(" | ")) if msg else ""
        head = (f'<p class="banner {E(st)}">{L["last_run"]} <bdi>#{run_row["id"]}</bdi>: <b>{E(L["outcome"].get(st, st))}</b> '
                f'{L["at"]} <bdi>{E(i18n.when(run_row["finished"]))}</bdi>{(" · <bdi>" + E(msg) + "</bdi>") if msg else ""}</p>')
    else:
        head = f'<p class="banner">{L["no_run"]}</p>'
    trs = ""
    for c in cov:
        bl = [i18n.reason(lang, x) for x in c["blocked"]]
        if c.get("disabled"):
            bl = [L["disabled"]]
        trs += (f'<tr><td>{E(c["source"])}</td><td>{i18n.num(lang, c["attempted"])}</td><td>{i18n.num(lang, c["succeeded"])}</td>'
                f'<td class="{"blocked" if c["blocked"] else ""}">{E("; ".join(bl) or "-")}</td><td>{i18n.num(lang, c["rows"])}</td>'
                f'<td><bdi>{E(L["never"] if c["last_success"] == "never" else i18n.when(c["last_success"]))}</bdi></td></tr>')
    yn = L["yes"] if p["remote_ok"] else L["no"]
    tips = "".join(f'<p class="tip">💡 {E(fa if lang == "fa" else en)}</p>' for _, en, fa in P.tips(p))

    res_info = ""
    if p.get("resume_skills"):
        res_info = f' · {L["resume_skills"]}: <bdi>{i18n.num(lang, len(p["resume_skills"]))} {L["skills_found"]}</bdi>'
    if p.get("linkedin_url"):
        res_info += f' · <a href="{E(p["linkedin_url"])}" target="_blank" rel="noopener">LinkedIn</a>'

    body = (f'{up_banner}<h1>{L["title"]}</h1><p>{L["profile"]}: <b><bdi>{E(p["name"] or L["unnamed"])}</bdi></b> · {L["roles"]}: <bdi>{E("، ".join(p["target_roles"]) if lang == "fa" else ", ".join(p["target_roles"]))}</bdi> · '
            f'{L["level"]}: {E(R.LV_FA.get(p["seniority"], p["seniority"]) if lang == "fa" else p["seniority"])} · '
            f'{L["places"]}: <bdi>{E(", ".join(p["locations"]) or L["any"])}</bdi> · {L["remote_ok"]}: {yn}{res_info}</p>{tips}{head}'
            f'<h2>{L["coverage"]}</h2><table><tr><th>{L["c_source"]}</th><th>{L["c_tried"]}</th><th>{L["c_ok"]}</th><th>{L["c_blocked"]}</th>'
            f'<th>{L["c_jobs"]}</th><th>{L["c_last"]}</th></tr>{trs}</table><p class="tip">{L["scope"]}</p>')
    if saved:
        body += f'<h2>{L["saved"]} ({i18n.num(lang, len(saved))})</h2>' + "".join(card(r, interactive, lang) for r in saved)
    body += f'<h2>{L["ranked"]} ({i18n.num(lang, len(rest))} {L["shown"]})</h2>' + ("".join(card(r, interactive, lang) for r in rest) or f'<p>{L["none_match"]}</p>')
    if unmatched:
        body += f'<p class="tip">{i18n.num(lang, unmatched)} {L["unmatched"]}</p>'
    if hidden:
        body += f'<details><summary>{L["hidden"]} ({i18n.num(lang, len(hidden))})</summary>' + "".join(card(r, interactive, lang) for r in hidden) + "</details>"
    body += _manual(p, lang) + _companies(lang)
    if not interactive:
        body += f'<p class="tip">{L["static"]}</p>'
    d = "rtl" if lang == "fa" else "ltr"
    js = (JS % json.dumps(L["save_failed"], ensure_ascii=False)) if interactive else ""
    return (f'<!doctype html><html lang="{lang}" dir="{d}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{L["title"]}</title><style>{CSS}</style><body>{body}{js}</body></html>')


def write_report(ws):
    d = pathlib.Path(ws) / "reports"
    d.mkdir(exist_ok=True)
    f = d / f"report-{dt.date.today().isoformat()}.html"
    h = render(ws)
    f.write_text(h, encoding="utf-8")
    (d / "latest.html").write_text(h, encoding="utf-8")
    return f


COLS = ["key", "state", "note", "score", "title", "company", "location", "work_mode", "employment", "salary", "source", "url", "also_on", "posted_at"]


def export(ws, fmt="csv"):
    _, rows = ranked(ws)
    for r in rows:
        r["also_on"] = " ".join(a["url"] for a in r["also_on"])
    if fmt == "json":
        return json.dumps([{k: r.get(k) for k in COLS} for r in rows], ensure_ascii=False, indent=2)
    b = io.StringIO()
    w = csv.DictWriter(b, COLS, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    return b.getvalue()


def make_handler(ws):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass

        def _send(self, code, body, ctype="text/html; charset=utf-8"):
            b = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.path == "/":
                self._send(200, render(ws, interactive=True))
            elif self.path == "/export.csv":
                self._send(200, export(ws, "csv"), "text/csv; charset=utf-8")
            elif self.path == "/export.json":
                self._send(200, export(ws, "json"), "application/json; charset=utf-8")
            else:
                self._send(404, "not found", "text/plain")

        def do_POST(self):
            if self.path != "/api/state":
                return self._send(404, "not found", "text/plain")
            try:
                b = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                c = store.conn(ws)
                store.set_state(c, b["key"], b.get("state"), b.get("note"))
                c.close()
                self._send(200, "{}", "application/json")
            except Exception as e:
                self._send(400, json.dumps({"error": str(e)}), "application/json")
    return H


def serve(ws, port=8765):
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(ws))   # localhost only
    return srv
