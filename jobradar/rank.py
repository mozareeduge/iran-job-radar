"""Transparent ranking: every point has a reason. Same corpus + different profile = different top."""
import re, datetime as dt

GENERIC = {"software", "engineer", "developer", "manager", "expert", "specialist", "senior", "junior", "lead", "کارشناس", "مهندس", "مدیر"}
LEVELS = {"junior": 0, "mid": 1, "senior": 2}
LEVEL_RE = [("junior", r"(junior|intern|trainee|entry|کارآموز|جونیور|مبتدی)"),
            ("senior", r"(senior|lead|principal|staff|head\s+of|ارشد|سنیور|لید)"),
            ("mid", r"(\bmid\b|intermediate|میان\s*پایه|متوسط)")]


def term_re(t):
    t = t.strip().lower()
    e = re.escape(t)
    if re.fullmatch(r"[a-z0-9 +#./-]+", t):
        return re.compile(r"(?<![a-z0-9])" + e + r"(?![a-z0-9])")
    return re.compile(e)


def level_of(text):
    for lv, p in LEVEL_RE:
        if re.search(p, text or "", re.I):
            return lv
    return None


def lang_of(text):
    s = (text or "")[:1500]
    fa = len(re.findall(r"[؀-ۿ]", s))
    la = len(re.findall(r"[A-Za-z]", s))
    return "fa" if fa > la else "en"


LV_FA = {"junior": "جونیور", "mid": "میانی", "senior": "ارشد"}
MODE_FA = {"remote": "دورکاری", "hybrid": "ترکیبی", "onsite": "حضوری"}


def rank_one(p, r, today=None):
    """Return (points, reasons_en, matched, reasons_fa, excluded). Every point carries a reason in both languages."""
    today = today or dt.date.today()
    title = (r["title"] or "").lower()
    jd = (r["jd"] or "").lower()
    pts, why, fa, best, bw, bf = 0, [], [], 0, "", ""
    for role in p["target_roles"]:
        role = role.strip().lower()
        if not role:
            continue
        toks = [x for x in re.split(r"\s+", role) if len(x) >= 2]
        core = [x for x in toks if x not in GENERIC]
        if term_re(role).search(title):
            v, w, wf = 40, f'title matches "{role}"', f"عنوان با «{role}» یکی است"
        elif core and all(term_re(x).search(title) for x in toks):
            v, w, wf = 28, f'title has all words of "{role}"', f"همهٔ کلمه‌های «{role}» در عنوان هست"
        elif any(len(x) >= 3 and term_re(x).search(title) for x in core):
            v, w, wf = 12, f'title shares a word with "{role}"', f"عنوان یک کلمه با «{role}» مشترک دارد"
        elif term_re(role).search(jd):
            v, w, wf = 8, f'description mentions "{role}"', f"در متن آگهی «{role}» آمده"
        else:
            continue
        if v > best:
            best, bw, bf = v, w, wf
    if best:
        pts += best
        why.append(f"{bw} (+{best})"); fa.append(f"{bf} (+{best})")
    else:
        pts -= 20
        why.append("no target role found in title or description (-20)"); fa.append("هیچ‌کدام از عنوان‌های شما در آگهی نیست (-20)")

    # Resume & LinkedIn skills match
    res_skills = [s.strip().lower() for s in (p.get("resume_skills") or []) if s.strip()]
    if res_skills:
        matched_sk = [sk for sk in res_skills if term_re(sk).search(title) or term_re(sk).search(jd)]
        if matched_sk:
            sk_pts = min(len(matched_sk) * 3, 15)
            pts += sk_pts
            top_sk = ", ".join(matched_sk[:4])
            if len(matched_sk) > 4:
                top_sk += f" (+{len(matched_sk)-4} more)"
            why.append(f"resume matches {len(matched_sk)} skills: {top_sk} (+{sk_pts})")
            fa.append(f"رزومه {len(matched_sk)} مهارت منطبق دارد: {top_sk} (+{sk_pts})")

    jl = level_of(f'{r["title"]} {r.get("seniority") or ""}')
    if jl:
        v = {0: 12, 1: -4, 2: -15}[abs(LEVELS[jl] - LEVELS[p["seniority"]])]
        pts += v
        why.append(f'level {jl} vs your {p["seniority"]} ({v:+d})')
        fa.append(f'سطح آگهی {LV_FA[jl]}، سطح شما {LV_FA.get(p["seniority"], p["seniority"])} ({v:+d})')
    loc = f'{r.get("location") or ""} {(r["jd"] or "")[:600]}'.lower()
    locs = [x.lower() for x in p["locations"] if x.strip()]
    mode = r.get("work_mode") or "unknown"
    if mode == "remote" and p["remote_ok"]:
        pts += 10
        why.append("remote and you accept remote (+10)"); fa.append("دورکاری است و شما دورکاری را قبول دارید (+10)")
    elif locs and any(x in loc for x in locs):
        pts += 8
        why.append("location matches (+8)"); fa.append("شهر با فهرست شما می‌خواند (+8)")
    elif locs and r.get("location"):
        pts -= 6
        why.append("location differs from your list (-6)"); fa.append("شهر در فهرست شما نیست (-6)")
    if p.get("remote_only") and mode != "remote":
        v = -10 if mode == "hybrid" else -25
        pts += v
        why.append(f"you want remote only; this is {mode} ({v:+d})")
        fa.append(f"شما فقط دورکاری می‌خواهید؛ این آگهی {MODE_FA.get(mode, 'نامشخص')} است ({v:+d})")
    if p["languages"]:
        lg = lang_of(f'{r["title"]} {r["jd"]}')
        lgf = "فارسی" if lg == "fa" else "انگلیسی"
        if lg in p["languages"]:
            pts += 2
            why.append(f"ad language {lg} is yours (+2)"); fa.append(f"زبان آگهی ({lgf}) را بلدید (+2)")
        else:
            pts -= 8
            why.append(f"ad language {lg} is not in your list (-8)"); fa.append(f"زبان آگهی ({lgf}) در فهرست شما نیست (-8)")
    emp = (r.get("employment") or "").lower()
    if p["employment"] and emp and emp not in [x.lower() for x in p["employment"]]:
        pts -= 10
        why.append(f"employment {emp} not in your list (-10)"); fa.append(f"نوع همکاری ({emp}) در فهرست شما نیست (-10)")
    try:
        age = (today - dt.date.fromisoformat((r.get("posted_at") or "")[:10])).days
        v = 5 if age <= 7 else 2 if age <= 30 else -5 if age > 90 else 0
        if v:
            pts += v
            why.append(f"posted {age} days ago ({v:+d})"); fa.append(f"{age} روز پیش منتشر شده ({v:+d})")
    except Exception:
        pass
    if r.get("live") == 0:
        pts -= 30
        why.append("ad is closed (-30)"); fa.append("آگهی بسته شده (-30)")
    excluded = ""
    for w in p.get("exclude_words") or []:
        w = w.strip().lower()
        if w and term_re(w).search(title):
            excluded = w
            why.append(f'title contains your excluded word "{w}"'); fa.append(f"عنوان کلمهٔ کنارگذاشته‌شدهٔ شما «{w}» را دارد")
            break
    return pts, why, best > 0, fa, excluded


def norm(s):
    return re.sub(r"[\W_]+", " ", (s or "").lower().replace("ي", "ی").replace("ك", "ک")).strip()


def rank(p, rows, today=None):
    """Score all rows (each needs a unique 'key'), merge duplicates (same normalized company+title), sort best first."""
    out = []
    for r in rows:
        s, why, match, why_fa, excl = rank_one(p, r, today)
        out.append(dict(r, score=s, why=why, why_fa=why_fa, matched=match, excluded=excl, also_on=[]))
    groups = {}
    for r in out:
        k = (norm(r["company"]), norm(r["title"]))
        if k[0] and k[1]:
            groups.setdefault(k, []).append(r)
    drop = set()
    for g in groups.values():
        if len(g) < 2:
            continue
        g.sort(key=lambda r: (r["score"], len(r["jd"] or "")), reverse=True)
        for o in g[1:]:
            g[0]["also_on"].append({"source": o["source"], "url": o["url"]})
            drop.add(o["key"])
    kept = [r for r in out if r["key"] not in drop]
    kept.sort(key=lambda r: (r["score"], r.get("posted_at") or "", r["title"]), reverse=True)
    return kept
