"""Neutral profile: what the person wants. No personal scoring is built in; everything that ranks comes from here."""
import json, pathlib, os

SCHEMA = "jobradar-profile/1"
TEMPLATE = {"schema": SCHEMA, "name": "", "ui_lang": "fa", "target_roles": [], "seniority": "mid", "locations": [],
            "remote_ok": True, "remote_only": False, "languages": ["fa", "en"], "employment": [], "exclude_words": [],
            "eligibility": "iran-resident"}
# ui_lang: fa (Persian, right-to-left, default) or en
# employment [] = any (full-time and part-time are treated the same)
# exclude_words: a job whose title contains one of these is hidden, with the reason shown
# remote_only: on-site and unknown-mode jobs drop to the bottom (kept, never deleted)

EXAMPLES = {
    "junior-qa": {"name": "Junior QA", "target_roles": ["qa engineer", "tester", "software tester", "quality assurance", "کنترل کیفیت", "تست نرم افزار"],
                  "seniority": "junior", "locations": ["تهران", "Tehran"], "remote_ok": True, "languages": ["fa", "en"]},
    "mid-designer": {"name": "Mid designer", "target_roles": ["ui designer", "ux designer", "product designer", "طراح رابط کاربری", "طراح محصول"],
                     "seniority": "mid", "locations": ["تهران", "Tehran"], "remote_ok": True, "languages": ["fa", "en"]},
    "senior-backend": {"name": "Senior backend", "target_roles": ["backend developer", "backend engineer", "python developer", "برنامه نویس بک اند"],
                       "seniority": "senior", "locations": ["تهران", "Tehran"], "remote_ok": True, "languages": ["fa", "en"]},
}


def workspace_path(arg=None):
    return pathlib.Path(arg or os.environ.get("JOBRADAR_WORKSPACE") or "workspace").resolve()


def make(example=None, roles=(), seniority=None, locations=(), remote_ok=None, name="", ui_lang=None, exclude=(), remote_only=None):
    p = json.loads(json.dumps(TEMPLATE))
    if example:
        p.update(json.loads(json.dumps(EXAMPLES[example])))
    if roles: p["target_roles"] = list(roles)
    if seniority: p["seniority"] = seniority
    if locations: p["locations"] = list(locations)
    if remote_ok is not None: p["remote_ok"] = remote_ok
    if remote_only is not None: p["remote_only"] = remote_only
    if name: p["name"] = name
    if ui_lang: p["ui_lang"] = ui_lang
    if exclude: p["exclude_words"] = list(exclude)
    return p


def save(ws, p):
    ws = pathlib.Path(ws); ws.mkdir(parents=True, exist_ok=True)
    (ws / "profile.json").write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")


def load(ws):
    f = pathlib.Path(ws) / "profile.json"
    if not f.exists():
        raise FileNotFoundError(f"No profile at {f}. Next step: python -m jobradar init   (it asks a few questions; Persian or English)")
    p = json.loads(f.read_text(encoding="utf-8"))
    for k, v in TEMPLATE.items(): p.setdefault(k, v)
    return p


def problems(p):
    out = []
    if not [r for r in p["target_roles"] if r.strip()]:
        out.append("profile.json has no target_roles. Next step: add at least one role, e.g. \"qa engineer\" and \"کنترل کیفیت\".")
    if p["seniority"] not in ("junior", "mid", "senior"):
        out.append("seniority must be junior, mid or senior.")
    if p.get("ui_lang") not in ("fa", "en"):
        out.append("ui_lang must be fa or en.")
    return out


def tips(p):
    """Advice that improves results; never blocks a run. Returns (id, english, persian)."""
    roles = [r for r in p["target_roles"] if r.strip()]
    has_fa = any(any("\u0600" <= ch <= "\u06ff" for ch in r) for r in roles)
    has_en = any(any("a" <= ch.lower() <= "z" for ch in r) for r in roles)
    out = []
    if roles and not has_fa:
        out.append(("fa_titles", "Add Persian titles too (e.g. «کنترل کیفیت»); many Iranian ads are written only in Persian.",
                    "عنوان‌های فارسی هم اضافه کنید (مثلاً «کنترل کیفیت»)؛ خیلی از آگهی‌های ایرانی فقط فارسی نوشته می‌شوند."))
    if roles and not has_en:
        out.append(("en_titles", "Add English titles too (e.g. \"QA engineer\"); tech ads often use English titles.",
                    "عنوان انگلیسی هم اضافه کنید (مثلاً QA engineer)؛ آگهی‌های فنی اغلب عنوان انگلیسی دارند."))
    if len(roles) > 8:
        out.append(("many", "More than 8 titles makes runs slow (each title is one search per site).",
                    "بیش از ۸ عنوان اجرا را کند می‌کند، چون هر عنوان در هر سایت یک جست‌وجوی جداست."))
    return out
