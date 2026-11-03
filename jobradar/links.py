"""Search links the person opens in their own browser, and the company careers list.
The radar never fetches these: their terms restrict automated collection (JobVision, Jobinja, LinkedIn)
or they are not machine-readable yet. Opening a normal search page yourself is ordinary use."""
import json, pathlib, urllib.parse as U

Q = U.quote

MANUAL = [
    # (id, Persian name, English name, url builder)
    ("jobvision", "جاب‌ویژن", "JobVision", lambda k: f"https://jobvision.ir/jobs/keyword/{Q(k)}"),
    ("jobinja", "جابینجا", "Jobinja", lambda k: f"https://jobinja.ir/jobs?filters%5Bkeywords%5D%5B0%5D={Q(k)}"),
    ("linkedin", "لینکدین", "LinkedIn", lambda k: f"https://www.linkedin.com/jobs/search/?keywords={Q(k)}&location=Iran"),
    ("eestekhdam", "ای‌استخدام", "e-estekhdam", lambda k: f"https://www.e-estekhdam.com/search/{Q(k)}"),
]


def manual_links(profile, limit_roles=4):
    roles = [r.strip() for r in profile.get("target_roles", []) if r.strip()][:limit_roles]
    return [{"id": i, "fa": fa, "en": en, "searches": [{"role": r, "url": f(r)} for r in roles]} for i, fa, en, f in MANUAL]


def companies():
    f = pathlib.Path(__file__).with_name("data") / "companies.json"
    return json.loads(f.read_text(encoding="utf-8"))["companies"]
