"""Workspace SQLite: observations (one row per source job), runs, run units, user state (save/hide/note)."""
import sqlite3, json, pathlib, datetime as dt

SCHEMA = """
create table if not exists observations(key text primary key, source text, source_id text, url text, title text, company text,
  location text, work_mode text, employment text, seniority text, salary text, posted_at text, expires_at text, live integer,
  jd text, first_seen text, last_seen text, run_id integer);
create table if not exists runs(id integer primary key autoincrement, started text, finished text, status text, summary text);
create table if not exists run_units(run_id integer, source text, unit text, status text, reason text, rows integer, ts text,
  primary key(run_id, source, unit));
create table if not exists user_state(key text primary key, state text, note text, updated text);
"""

def now(): return dt.datetime.now().isoformat(timespec="seconds")

def db_path(ws): return pathlib.Path(ws) / "jobradar.db"

def conn(ws):
    pathlib.Path(ws).mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(db_path(ws)); c.row_factory = sqlite3.Row; c.executescript(SCHEMA); return c

def obs_key(r): return f'{r["source"]}:{r["source_id"]}'

def upsert(c, rows, run_id=None):
    t = now(); n_new = 0
    for r in rows:
        k = obs_key(r); old = c.execute("select first_seen from observations where key=?", (k,)).fetchone()
        n_new += 0 if old else 1
        c.execute("""insert or replace into observations(key,source,source_id,url,title,company,location,work_mode,employment,seniority,
          salary,posted_at,expires_at,live,jd,first_seen,last_seen,run_id) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (k, r["source"], r["source_id"], r["url"], r["title"], r.get("company", ""), r.get("location", ""), r.get("work_mode", "unknown"),
                   r.get("employment", ""), r.get("seniority", ""), r.get("salary", ""), r.get("posted_at", ""), r.get("expires_at", ""),
                   None if r.get("live") is None else int(bool(r["live"])), r.get("jd", ""), old[0] if old else t, t, run_id))
    c.commit(); return n_new

def known_keys(c): return {r[0] for r in c.execute("select key from observations")}

def set_state(c, key, state=None, note=None):
    if state not in (None, "saved", "hidden", "none"): raise ValueError("state must be saved, hidden or none")
    cur = c.execute("select state,note from user_state where key=?", (key,)).fetchone()
    st = (cur["state"] if cur else "none") if state is None else state
    nt = (cur["note"] if cur else "") if note is None else note
    c.execute("insert or replace into user_state(key,state,note,updated) values(?,?,?,?)", (key, st, nt, now())); c.commit()

def states(c): return {r["key"]: dict(r) for r in c.execute("select * from user_state")}

def all_obs(c): return [dict(r) for r in c.execute("select * from observations")]
