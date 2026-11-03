import pytest, pathlib
from jobradar import resume as RS, rank as R, profile as P, updater as UP, cli


def test_extract_skills_from_text():
    text = """
    Software Engineer with experience in Python, FastAPI, Docker, and PostgreSQL.
    Also worked on React, Tailwind, Git, and automated testing with pytest.
    تجربه در طراحی رابط کاربری و تست نرم‌افزار.
    """
    skills = RS.extract_skills(text)
    assert "python" in skills
    assert "fastapi" in skills
    assert "docker" in skills
    assert "postgresql" in skills
    assert "react" in skills
    assert "تست نرم‌افزار" in skills


def test_normalize_linkedin_url():
    assert RS.normalize_linkedin_url("https://www.linkedin.com/in/johndoe") == "https://www.linkedin.com/in/johndoe"
    assert RS.normalize_linkedin_url("linkedin.com/in/johndoe") == "https://linkedin.com/in/johndoe"
    assert RS.normalize_linkedin_url("johndoe") == "https://www.linkedin.com/in/johndoe/"
    assert RS.normalize_linkedin_url("") == ""


def test_ranking_with_resume_skills():
    p = P.make("junior-qa", roles=["qa engineer"], seniority="junior")
    p["resume_skills"] = ["selenium", "postman", "python", "docker"]

    ad = {
        "key": "test:1",
        "title": "Junior QA Engineer",
        "company": "Tech Corp",
        "jd": "Looking for QA with experience in Python, Selenium and Postman.",
        "location": "Tehran",
        "work_mode": "remote",
        "seniority": "junior",
        "languages": ["en"],
        "employment": "full-time",
        "url": "https://example.com/1"
    }

    pts, why, matched, why_fa, excluded = R.rank_one(p, ad)
    assert matched is True
    # Should have bonus for resume matching skills
    assert any("resume matches" in w for w in why)
    assert any("رزومه" in w for w in why_fa)


def test_updater_semver_and_offline():
    assert UP.is_newer("0.2.0", "0.1.0") is True
    assert UP.is_newer("0.1.1", "0.1.0") is True
    assert UP.is_newer("0.1.0", "0.1.0") is False
    assert UP.is_newer("0.0.9", "0.1.0") is False

    # check_update with non-existent or mock
    res = UP.check_update(ws=None, force=False, timeout=0.1)
    assert "has_update" in res
    assert "current_version" in res


def test_cli_resume_and_linkedin(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    # init workspace
    cli.main(["--workspace", str(ws), "init", "--example", "junior-qa"])

    # add resume text
    cli.main(["--workspace", str(ws), "resume", "Skilled in Python, Docker, React, and Git."])
    p = P.load(ws)
    assert "python" in p["resume_skills"]
    assert "docker" in p["resume_skills"]

    # add custom skill
    cli.main(["--workspace", str(ws), "resume", "--add-skill", "kubernetes, postgresql"])
    p = P.load(ws)
    assert "kubernetes" in p["resume_skills"]
    assert "postgresql" in p["resume_skills"]

    # set linkedin url
    cli.main(["--workspace", str(ws), "linkedin", "https://linkedin.com/in/myprofile"])
    p = P.load(ws)
    assert p["linkedin_url"] == "https://linkedin.com/in/myprofile"

    # clear resume
    cli.main(["--workspace", str(ws), "resume", "--clear"])
    p = P.load(ws)
    assert p["resume_skills"] == []

    # clear linkedin
    cli.main(["--workspace", str(ws), "linkedin", "--clear"])
    p = P.load(ws)
    assert p["linkedin_url"] == ""
