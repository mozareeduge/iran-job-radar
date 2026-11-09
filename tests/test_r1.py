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
    if "jobinja.ir/companies/" in url:
        return Resp(200, JOBINJA_DETAIL)
    if "jobinja" in url:
        kwd = (kw.get("params") or {}).get("filters[keywords][0]", "")
        return Resp(200, jobinja_page(10 if kwd == "qa engineer" else 20) if (kw.get("params") or {}).get("page") == 1 else "<html></html>")
    if "JobPost/Detail" in url:
        return Resp(200, "{}", {"data": {"description": "<p>Write <b>test plans</b></p>", "requirements": "selenium"}})
    if "jobvision" in url:
        return Resp(200, "{}", {"data": {"jobPosts": [jobvision_post(500 + len(str(kw.get("json"))))], "jobPostCount": 1}})
    return Resp(404)


def jobinja_page(n):
    return "<ul>" + "".join(
        f'''<li class="o-listView__item c-jobListView__item"><h2><a class="c-jobListView__titleLink" href="https://jobinja.ir/companies/acme/jobs/Ab{n}/qa-engineer?_ref=16">QA Engineer {n}</a></h2>
        <ul><li class="c-jobListView__metaItem"><i class="c-icon c-icon--construction"></i><span>شرکت آکمه</span></li>
        <li class="c-jobListView__metaItem"><i class="c-icon c-icon--place"></i><span>تهران ، تهران</span></li>
        <li class="c-jobListView__metaItem"><i class="c-icon c-icon--resume"></i><span>قراردادی</span></li></ul></li>''' for n in (n, n + 1)) + "</ul>"


JOBINJA_DETAIL = '''<html><script type="application/ld+json">{"@context":"https://schema.org","@type":"JobPosting","title":"QA Engineer",
"datePosted":"2026-11-01T10:00:00+03:30","validThrough":"2099-01-01","description":"&lt;p&gt;Manual and automated testing&lt;/p&gt;",
"hiringOrganization":{"@type":"Organization","name":"Acme"},"employmentType":"FULL_TIME"}</script>
<ul><li class="c-infoBox__item"><h4 class="c-infoBox__itemTitle">موقعیت مکانی</h4><div class="tags"><span class="c-infoBox__itemTags">تهران</span></div></li>
<li class="c-infoBox__item"><h4 class="c-infoBox__itemTitle">نوع همکاری</h4><div><span class="c-infoBox__itemTags">تمام وقت</span></div></li>
<li class="c-infoBox__item"><h4 class="c-infoBox__itemTitle">حقوق</h4><div><span class="c-infoBox__itemTags">توافقی</span></div></li></ul></html>'''


def jobvision_post(i, **kw):
    d = {"id": i, "title": f"QA Engineer {i}", "company": {"id": 9, "nameFa": "آکمه", "nameEn": "Acme"},
         "location": {"province": {"titleFa": "تهران"}, "city": {"titleFa": "تهران"}}, "workType": {"titleFa": "تمام وقت"},
         "salary": {"titleFa": "توافقی"}, "activationTime": {"date": "2026-11-05T09:00:00", "beautifyFa": "۳ روز پیش"}, "isRemote": False}
    d.update(kw)
    return d


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
    n_units = len(P.load(ws)["target_roles"]) * len(C.UNITS)
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
    assert "Coverage" in page and "Quera Magnet" in page and "JobVision" in page and "Jobinja" in page and "Jobvision" not in page
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


def test_unknown_source_refused(tmp_path):
    ws = ws_with_profile(tmp_path)
    with pytest.raises(ValueError):
        runner.run(ws, P.load(ws), FakeHttp(ok_handler), sources=["linkedin"], log=lambda *a: None)


def test_jobinja_list_and_detail():
    http = FakeHttp(ok_handler)
    rows = C.jobinja_unit(http, "qa engineer", details=1)
    assert [r["source_id"] for r in rows] == ["jj-Ab10", "jj-Ab11"]
    a, b = rows
    assert a["url"] == "https://jobinja.ir/companies/acme/jobs/Ab10/qa-engineer"      # tracking query dropped
    assert a["company"] == "Acme" and a["location"] == "تهران" and a["salary"] == "توافقی" and a["posted_at"] == "2026-11-01"
    assert "automated testing" in a["jd"] and a["live"] is True
    assert b["company"] == "شرکت آکمه" and b["location"] == "تهران ، تهران" and b["jd"] == ""   # list-only row past the detail limit
    assert http.calls[0][2] == {"filters[keywords][0]": "qa engineer", "page": 1}
    again = C.jobinja_unit(FakeHttp(ok_handler), "qa engineer", known={"Jobinja:jj-Ab10"})
    assert [r["source_id"] for r in again] == ["jj-Ab11"] and again.seen == 1        # stored rows are not re-read or blanked


def test_jobinja_expired_detail_marked_closed():
    def h(u, k, kw):
        return Resp(200, "<html><h1>QA</h1><div class='alert'>این آگهی منقضی شده است</div></html>") if "/companies/" in u else ok_handler(u, k, kw)
    assert C.jobinja_unit(FakeHttp(h), "qa engineer", details=1)[0]["live"] is False


def test_jobvision_list_and_detail():
    http = FakeHttp(ok_handler)
    rows = C.jobvision_unit(http, "qa engineer")
    r = rows[0]
    assert r["source"] == "JobVision" and r["url"] == f"https://jobvision.ir/jobs/{r['source_id'][3:]}"
    assert r["company"] == "آکمه" and r["location"] == "تهران" and r["employment"] == "تمام وقت" and r["salary"] == "توافقی"
    assert r["posted_at"] == "2026-11-05" and "test plans" in r["jd"] and "selenium" in r["jd"]
    assert http.calls[0][0] == "post" and http.calls[0][2]["keyword"] == "qa engineer"


def test_jobvision_remote_and_unexpected_format():
    h = lambda u, k, kw: Resp(200, "{}", {"data": {"jobPosts": [jobvision_post(1, isRemote=True)]}}) if "List" in u else Resp(404)
    assert C.jobvision_unit(FakeHttp(h), "x")[0]["work_mode"] == "remote"
    with pytest.raises(C.Blocked, match="unexpected page format"):
        C.jobvision_unit(FakeHttp(lambda u, k, kw: Resp(200, "<html>app</html>")), "x")
    with pytest.raises(C.Blocked, match="http 403"):
        C.jobinja_unit(FakeHttp(lambda u, k, kw: Resp(403)), "x")


def test_part_time_normalised():
    assert C.norm_row(title="x", employment="تمام وقت یا پاره وقت")["employment"] == "part-time"
