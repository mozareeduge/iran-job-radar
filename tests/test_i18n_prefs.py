import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from jobradar import profile as P, store, rank as R, report as RP, cli, links


def job(key, title, **kw):
    d = dict(key=key, source="Quera Magnet", source_id=key, url=f"https://example.org/{key}", title=title, company="Co", location="Tehran",
             work_mode="onsite", employment="", seniority="", salary="", posted_at="", expires_at="", live=1, jd="")
    d.update(kw)
    return d


def seed(ws, p, rows):
    P.save(ws, p)
    c = store.conn(ws)
    store.upsert(c, [{k: v for k, v in r.items() if k != "key"} for r in rows])
    c.close()


def test_persian_report_is_rtl_with_persian_reasons(tmp_path):
    p = P.make("junior-qa", ui_lang="fa")
    seed(tmp_path, p, [job("a", "کارشناس کنترل کیفیت")])
    h = RP.render(tmp_path)
    assert '<html lang="fa" dir="rtl">' in h
    assert "رادار شغلی" in h and "چرا این رتبه" in h
    assert "عنوان با «کنترل کیفیت» یکی است" in h
    assert "جاب‌ویژن" in h and "jobvision.ir/jobs/keyword/" in h     # manual links shown
    assert "دیجی‌کالا" in h                                            # company pages shown


def test_english_report_when_chosen(tmp_path):
    p = P.make("junior-qa", ui_lang="en")
    seed(tmp_path, p, [job("a", "QA Engineer")])
    h = RP.render(tmp_path)
    assert 'dir="ltr"' in h and "Job Radar" in h and 'title matches &quot;qa engineer&quot;' in h


def test_exclude_words_hide_with_reason():
    p = P.make("junior-qa", exclude=["sales"])
    rows = R.rank(p, [job("a", "QA Engineer"), job("b", "QA engineer sales support")])
    b = [r for r in rows if r["key"] == "b"][0]
    assert b["excluded"] == "sales"
    assert any("excluded word" in w for w in b["why"]) and any("کنارگذاشته" in w for w in b["why_fa"])


def test_remote_only_pushes_onsite_down():
    base = P.make("junior-qa")
    ronly = P.make("junior-qa", remote_only=True)
    rows = [job("on", "QA Engineer", work_mode="onsite"), job("re", "QA Engineer tester", work_mode="remote")]
    assert R.rank(ronly, rows)[0]["key"] == "re"
    s_base = {r["key"]: r["score"] for r in R.rank(base, rows)}
    s_ro = {r["key"]: r["score"] for r in R.rank(ronly, rows)}
    assert s_ro["on"] == s_base["on"] - 25


def test_wizard_in_persian_with_persian_answers():
    answers = iter(["تست‌نویس", "کنترل کیفیت، QA engineer", "۱", "تهران", "بله", "نه", "فروش"])
    p = cli.wizard("fa", inp=lambda _: next(answers))
    assert p["ui_lang"] == "fa" and p["seniority"] == "junior"
    assert p["target_roles"] == ["کنترل کیفیت", "QA engineer"]       # Persian comma accepted
    assert p["remote_ok"] is True and p["remote_only"] is False and p["exclude_words"] == ["فروش"]


def test_wizard_reasks_when_no_role():
    answers = iter(["", "", "QA engineer", "", "", "", "", ""])
    p = cli.wizard("en", inp=lambda _: next(answers))
    assert p["target_roles"] == ["QA engineer"] and p["seniority"] == "mid"


def test_prefs_changes_without_editing_json(tmp_path, capsys):
    P.save(tmp_path, P.make("junior-qa"))
    assert cli.main(["-w", str(tmp_path), "prefs", "--lang", "en", "--remote-only", "yes", "--exclude", "sales"]) == 0
    p = P.load(tmp_path)
    assert p["ui_lang"] == "en" and p["remote_only"] and p["exclude_words"] == ["sales"]


def test_tips_ask_for_both_scripts():
    ids = [t[0] for t in P.tips(P.make(roles=["qa engineer"]))]
    assert "fa_titles" in ids
    ids = [t[0] for t in P.tips(P.make(roles=["کنترل کیفیت"]))]
    assert "en_titles" in ids


def test_company_list_is_wellformed():
    cs = links.companies()
    assert len(cs) >= 10
    for c in cs:
        assert c["url"].startswith("https://") and c["name"] and c["name_fa"]


def test_no_personal_data_in_repo():
    root = pathlib.Path(__file__).resolve().parent.parent
    bad = ["235217824", "C:/Users/Zarinpal", "C:\\Users\\Zarinpal", "OM-", "mission-evidence"]
    for f in root.rglob("*"):
        if f.is_file() and f.suffix in (".py", ".md", ".json", ".toml", ".txt", ".cff") and ".venv" not in f.parts and f.name != "test_i18n_prefs.py":
            t = f.read_text(encoding="utf-8", errors="ignore")
            for b in bad:
                assert b not in t, f"{b} in {f}"


def test_rerun_counts_already_stored_jobs_not_as_empty():
    from jobradar import collectors as C
    html = '<a href="https://karboom.io/jobs/abc12/qa-engineer">x</a>'
    class H:
        def get(self, url, **kw):
            class R: status_code = 200; text = html
            return R()
    rows = C.karboom_unit(H(), "qa", known={"Karboom:kb-abc12"})
    assert len(rows) == 0 and rows.seen == 1
