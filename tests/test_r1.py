import json, threading, urllib.request, pathlib, sqlite3, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import pytest
from jobradar import profile as P, store, runner, rank as R, report as RP, collectors as C, cli


class Resp:
    def __init__(self, code=200, text="", js=None):
        self.status_code, self.text, self._js = code, text, js

    def json(self):
        if self._js is None:
            raise ValueError("not json")
        return self._js


def quera_page(n_jobs, start=0):
    edges = [{"node": {"pk": start + i, "title": f"QA Engineer {start + i}", "company": {"name": f"Co{start + i}"}, "city": {"name": "Tehran"}, "open": True}} for i in range(n_jobs)]
    return '<script id="__NEXT_DATA__" type="application/json">' + json.dumps({"props": {"pageProps": {"jobs": {"edges": edges}}}}) + "</script>"


class FakeHttp:
    """Routes by URL substring. handler(url, kind) -> Resp. Records calls."""
    def __init__(self, handler):
        self.handler, self.calls = handler, []

    def get(self, url, **kw):
        self.calls.append(("get", url, kw.get("params")))
        return self.handler(url, "get", kw)

    def post(self, url, **kw):
        self.calls.append(("post", url, kw.get("json")))
        return self.handler(url, "post", kw)


def ok_handler(url, kind, kw):
    if "quera.org/magnet/jobs/" in url:
        return Resp(500)  # detail optional
    if "quera.org" in url:
        kwd = (kw.get("params") or {}).get("search", "")
        return Resp(200, quera_page(2, start=100 if kwd == "qa engineer" else 200))
    if "irantalent" in url:
        return Resp(200, "{}", {"data": {"data": [{"id": 7, "title": "Tester", "slug": "t", "brand_data": {"name_en": "Acme"}, "role_description": "test things",
                                                    "location_text_farsi": "تهران", "work_type": "on_site", "employment_type": {"title": "Part-time"}}], "last_page": 1}})
    if "karboom" in url:
        return Resp(200, "<html>no results</html>")
    return Resp(404)


def ws_with_profile(tmp_path, example="junior-qa"):
    ws = tmp_path / "ws"
    P.save(ws, P.make(example, ui_lang="en"))   # English UI here; Persian UI is covered in test_i18n_prefs.py
    return ws


def stored(ws):
    c = store.conn(ws)
    return sorted(r[0] for r in c.execute("select key from observations"))


def test_403_is_blocked_and_named(tmp_path):
    ws = ws_with_profile(tmp_path)
    res = runner.run(ws, P.load(ws), FakeHttp(lambda u, k, kw: Resp(403, "forbidden")), log=lambda *a: None)
    assert res["outcome"] == "blocked"
    assert "http 403" in res["message"] and "Quera Magnet" in res["message"]
    assert all(v["status"] == "blocked" for v in res["sources"].values())


def test_login_wall_is_named(tmp_path):
    ws = ws_with_profile(tmp_path)
    page = '<html><form action="/accounts/login"><input type="password" name="password"></form></html>'
    res = runner.run(ws, P.load(ws), FakeHttp(lambda u, k, kw: Resp(200, page)), sources=["quera"], log=lambda *a: None)
    assert res["outcome"] == "blocked" and "login wall" in res["message"]


def test_partial_names_the_blocked_source(tmp_path):
    ws = ws_with_profile(tmp_path)
    def h(u, k, kw):
        return Resp(403) if "karboom" in u else ok_handler(u, k, kw)
    res = runner.run(ws, P.load(ws), FakeHttp(h), log=lambda *a: None)
    assert res["outcome"] == "partial"
    assert "Karboom: http 403" in res["message"] and res["sources"]["quera"]["status"] == "ok"
    run_row, cov = runner.coverage(ws)
    assert {c["source"]: c["blocked"] for c in cov}["Karboom"] == ["http 403 (access refused)"]


def test_empty_result_is_not_silent(tmp_path):
    ws = ws_with_profile(tmp_path)
    res = runner.run(ws, P.load(ws), FakeHttp(lambda u, k, kw: Resp(200, "<html>no results</html>")), sources=["karboom"], log=lambda *a: None)
    assert res["outcome"] == "succeeded" and "returned 0 jobs" in res["message"]


def test_cancel_then_resume_no_duplicates(tmp_path):
    full = ws_with_profile(tmp_path / "a")
    runner.run(full, P.load(full), FakeHttp(ok_handler), log=lambda *a: None)
    ws = ws_with_profile(tmp_path / "b")
    p = P.load(ws)
    r1 = runner.run(ws, p, FakeHttp(ok_handler), stop_after_units=3, log=lambda *a: None)
    assert r1["outcome"] == "cancelled"
    partial = stored(ws)
    assert 0 < len(partial) < len(stored(full))
    http2 = FakeHttp(ok_handler)
    r2 = runner.run(ws, p, http2, resume=True, log=lambda *a: None)
    assert r2["outcome"] == "succeeded" and r2["run_id"] == r1["run_id"]
    assert stored(ws) == stored(full)               # same set, no dupes (key is primary key)
    n_units = len(P.load(ws)["target_roles"]) * 3
    assert len(http2.calls) < n_units * 3            # done units were not asked again
    c = store.conn(ws)
    assert c.execute("select count(*) from runs").fetchone()[0] == 1


def test_resume_retries_blocked_units(tmp_path):
    ws = ws_with_profile(tmp_path)
    p = P.load(ws)
    r1 = runner.run(ws, p, FakeHttp(lambda u, k, kw: Resp(429)), sources=["quera"], log=lambda *a: None)
    assert r1["outcome"] == "blocked"
    # a finished run is not resumed; a new run starts
    r2 = runner.run(ws, p, FakeHttp(ok_handler), sources=["quera"], resume=True, log=lambda *a: None)
    assert r2["outcome"] == "succeeded" and r2["run_id"] != r1["run_id"]


CORPUS = [
    dict(key="x:1", source="Quera Magnet", source_id="1", url="u1", title="Junior QA Engineer", company="A", location="Tehran", work_mode="onsite", employment="full-time", seniority="", salary="", posted_at="", expires_at="", live=1, jd="manual and automated testing"),
    dict(key="x:2", source="IranTalent", source_id="2", url="u2", title="Senior Backend Developer (Python)", company="B", location="Tehran", work_mode="onsite", employment="full-time", seniority="", salary="", posted_at="", expires_at="", live=1, jd="django services, python"),
    dict(key="x:3", source="Karboom", source_id="3", url="u3", title="UI/UX Designer", company="C", location="Tehran", work_mode="hybrid", employment="part-time", seniority="", salary="", posted_at="", expires_at="", live=1, jd="product designer figma ux designer"),
    dict(key="x:4", source="Karboom", source_id="4", url="u4", title="Sales Expert", company="D", location="Tehran", work_mode="onsite", employment="full-time", seniority="", salary="", posted_at="", expires_at="", live=1, jd="selling"),
    dict(key="x:5", source="Quera Magnet", source_id="5", url="u5", title="Senior QA Engineer", company="E", location="Tehran", work_mode="onsite", employment="full-time", seniority="", salary="", posted_at="", expires_at="", live=1, jd="lead the QA team"),
]


def test_three_profiles_get_different_top_results():
    tops = {}
    for ex in P.EXAMPLES:
        tops[ex] = R.rank(P.make(ex), CORPUS)[0]["key"]
    assert tops == {"junior-qa": "x:1", "mid-designer": "x:3", "senior-backend": "x:2"}
    assert len(set(tops.values())) == 3


def test_ranking_shows_reasons_and_part_time_not_penalised():
    top = R.rank(P.make("mid-designer"), CORPUS)[0]
    assert top["employment"] == "part-time" and any("title" in w for w in top["why"]) and not any("employment" in w for w in top["why"])


def test_duplicates_merged():
    d = dict(CORPUS[0], key="y:1", source="IranTalent", url="other")
    rows = R.rank(P.make("junior-qa"), CORPUS + [d])
    assert sum(1 for r in rows if r["title"] == "Junior QA Engineer") == 1
    assert [r for r in rows if r["title"] == "Junior QA Engineer"][0]["also_on"]


def test_saved_hidden_notes_survive_rerun(tmp_path):
    ws = ws_with_profile(tmp_path)
    p = P.load(ws)
    runner.run(ws, p, FakeHttp(ok_handler), log=lambda *a: None)
    c = store.conn(ws)
    k1, k2 = stored(ws)[:2]
    store.set_state(c, k1, "saved", "call them")
    store.set_state(c, k2, "hidden")
    runner.run(ws, p, FakeHttp(ok_handler), log=lambda *a: None)       # fresh re-run
    st = store.states(store.conn(ws))
    assert st[k1]["state"] == "saved" and st[k1]["note"] == "call them" and st[k2]["state"] == "hidden"
    page = RP.render(ws)
    assert "call them" in page and "Saved" in page and "Hidden (1)" in page
    assert "Coverage" in page and "Quera Magnet" in page and "Jobvision" in page
    csv_txt = RP.export(ws, "csv")
    assert "saved" in csv_txt and "call them" in csv_txt
    assert json.loads(RP.export(ws, "json"))


def test_serve_state_roundtrip(tmp_path):
    ws = ws_with_profile(tmp_path)
    runner.run(ws, P.load(ws), FakeHttp(ok_handler), log=lambda *a: None)
    k = stored(ws)[0]
    srv = RP.serve(ws, 0)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/state", data=json.dumps({"key": k, "state": "saved", "note": "n1"}).encode(), headers={"Content-Type": "application/json"})
        assert urllib.request.urlopen(req).status == 200
        html = urllib.request.urlopen(f"http://127.0.0.1:{port}/").read().decode()
        assert "setState" in html and "n1" in html
        assert urllib.request.urlopen(f"http://127.0.0.1:{port}/export.csv").status == 200
    finally:
        srv.shutdown()
    assert store.states(store.conn(ws))[k]["state"] == "saved"


def test_run_refuses_without_roles(tmp_path, capsys):
    ws = tmp_path / "ws"
    assert cli.main(["-w", str(ws), "init"]) == 0
    assert cli.main(["-w", str(ws), "run"]) == 2
    assert "no target_roles" in capsys.readouterr().out


def test_disabled_sources_refused(tmp_path):
    ws = ws_with_profile(tmp_path)
    with pytest.raises(ValueError):
        runner.run(ws, P.load(ws), FakeHttp(ok_handler), sources=["jobvision"], log=lambda *a: None)


def test_part_time_normalised():
    assert C.norm_row(title="x", employment="تمام وقت یا پاره وقت")["employment"] == "part-time"
