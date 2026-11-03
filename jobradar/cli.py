"""python -m jobradar <start|doctor|init|prefs|run|rank|report|serve|links|export|mark|note>"""
import argparse, sys, json, pathlib, sqlite3
from . import profile as P, store, collectors as C, runner, report as RP, rank as R, links as LK

PROBES = {"quera": "https://quera.org/magnet/jobs", "irantalent": "https://www.irantalent.com/", "karboom": "https://karboom.io/jobs"}


def out(*a): print(*a, flush=True)


def doctor(a):
    bad, steps = 0, []
    v = sys.version_info
    out(f"[{'ok' if v >= (3, 9) else 'FAIL'}] python {v.major}.{v.minor}.{v.micro} (need 3.9+)")
    if v < (3, 9): bad += 1; steps.append("Install Python 3.9 or newer.")
    for m in ("requests", "bs4"):
        try: __import__(m); out(f"[ok] module {m}")
        except ImportError: bad += 1; out(f"[FAIL] module {m} missing"); steps.append("pip install requests beautifulsoup4")
    ws = P.workspace_path(a.workspace)
    try:
        ws.mkdir(parents=True, exist_ok=True); t = ws / ".write-test"; t.write_text("x"); t.unlink(); out(f"[ok] workspace writable: {ws}")
    except Exception as e:
        bad += 1; out(f"[FAIL] workspace not writable: {ws} ({e})"); steps.append("Pass --workspace <a folder you can write to>.")
    if (ws / "profile.json").exists(): out("[ok] profile.json present")
    else: out("[note] no profile yet"); steps.append("python -m jobradar init --example junior-qa   (or --role \"your role\")")
    if a.offline: out("[skip] network check (--offline)")
    else:
        http = C.Http(delay=0.5, timeout=12)
        for s, u in PROBES.items():
            try:
                r = C.call(http.get, u)
                out(f"[ok] {C.NAMES[s]} reachable (http {r.status_code})")
            except C.Blocked as e:
                out(f"[warn] {C.NAMES[s]}: {e.reason}. The run will name it as blocked; the other sources still run.")
        for s, why in C.DISABLED.items(): out(f"[off] {s}: {why}")
    steps.append("python -m jobradar run   then   python -m jobradar report")
    out("\nNext steps:"); [out(f"  {i}. {s}") for i, s in enumerate(steps, 1)]
    return 1 if bad else 0


Q = {
    "fa": {"name": "اسم این پروفایل (اختیاری، مثلاً «تست‌نویس جونیور»): ",
           "roles": "چه شغل‌هایی می‌خواهید؟ عنوان‌ها را با ویرگول جدا کنید؛ فارسی و انگلیسی هر دو را بنویسید\n  (مثلاً: کنترل کیفیت, تست نرم افزار, QA engineer): ",
           "level": "سطح شما؟ [1] جونیور  [2] میانی  [3] ارشد  (پیش‌فرض ۲): ",
           "places": "کدام شهرها؟ با ویرگول (مثلاً: تهران, Tehran). خالی = هر جا: ",
           "remote": "دورکاری قبول است؟ [ب]له / [ن]ه (پیش‌فرض بله): ",
           "remote_only": "فقط دورکاری؟ [ب]له / [ن]ه (پیش‌فرض نه): ",
           "exclude": "کلمه‌هایی که نمی‌خواهید در عنوان باشد (مثلاً: فروش, بازاریابی). خالی = هیچ: ",
           "need_role": "دست‌کم یک عنوان شغلی لازم است."},
    "en": {"name": "Name for this profile (optional, e.g. \"Junior QA\"): ",
           "roles": "Which jobs? Separate titles with commas; give both English and Persian if you can\n  (e.g. QA engineer, software tester, کنترل کیفیت): ",
           "level": "Your level? [1] junior  [2] mid  [3] senior  (default 2): ",
           "places": "Which cities? Comma separated (e.g. Tehran, تهران). Empty = anywhere: ",
           "remote": "Is remote OK? [y]es / [n]o (default yes): ",
           "remote_only": "Remote only? [y]es / [n]o (default no): ",
           "exclude": "Words you do NOT want in a title (e.g. sales, marketing). Empty = none: ",
           "need_role": "At least one job title is needed."},
}
YES = {"y", "yes", "ب", "بله", "آره", "اره", "1"}
NO = {"n", "no", "ن", "نه", "خیر", "0"}


def split(s):
    return [x.strip() for x in s.replace("،", ",").split(",") if x.strip()]


def ask(prompt, inp):
    try:
        return inp(prompt).strip()
    except EOFError:
        return ""


def yesno(v, default):
    v = v.strip().lower()
    return True if v in YES else False if v in NO else default


def wizard(lang, inp=input):
    """Ask the person, in their language, only what changes the results. Agents can skip this with flags."""
    q = Q[lang]
    name = ask(q["name"], inp)
    roles = []
    for _ in range(3):
        roles = split(ask(q["roles"], inp))
        if roles:
            break
        out(q["need_role"])
    lv = {"1": "junior", "2": "mid", "3": "senior", "۱": "junior", "۲": "mid", "۳": "senior",
          "junior": "junior", "mid": "mid", "senior": "senior", "جونیور": "junior", "میانی": "mid", "ارشد": "senior"}.get(ask(q["level"], inp).lower(), "mid")
    places = split(ask(q["places"], inp))
    remote = yesno(ask(q["remote"], inp), True)
    ronly = yesno(ask(q["remote_only"], inp), False) if remote else False
    excl = split(ask(q["exclude"], inp))
    return P.make(None, roles, lv, places, remote, name=name, ui_lang=lang, exclude=excl, remote_only=ronly)


def pick_lang(a, inp=input):
    if a.lang:
        return a.lang
    if not sys.stdin.isatty():
        return "fa"
    v = ask("Language / زبان:  [1] فارسی   [2] English  (پیش‌فرض/default 1): ", inp).lower()
    return "en" if v in ("2", "en", "english", "e", "۲", "انگلیسی") else "fa"


def init(a):
    ws = P.workspace_path(a.workspace)
    if (ws / "profile.json").exists() and not a.force:
        out(f"profile already exists at {ws / 'profile.json'} (use --force to overwrite, or: python -m jobradar prefs)"); return 1
    lang = pick_lang(a)
    flags = a.example or a.role or a.seniority or a.location
    if not flags and sys.stdin.isatty():
        p = wizard(lang)
    else:
        p = P.make(a.example, a.role, a.seniority, a.location, name=a.name, ui_lang=lang, exclude=a.exclude,
                   remote_only=True if a.remote_only else None, remote_ok=False if a.no_remote else None)
    P.save(ws, p); store.conn(ws).close()
    out(f"workspace ready: {ws}\nprofile: {ws / 'profile.json'}")
    show_prefs(p)
    for m in P.problems(p): out("TODO: " + m)
    for _, en, fa in P.tips(p): out("tip: " + (fa if lang == "fa" else en))
    out(("قدم بعد" if lang == "fa" else "Next step") + ": python -m jobradar run")
    return 0


def show_prefs(p):
    lang = p.get("ui_lang", "fa")
    if lang == "fa":
        out(f"  زبان: فارسی | عنوان‌ها: {'، '.join(p['target_roles'])} | سطح: {p['seniority']} | شهرها: {', '.join(p['locations']) or 'هر جا'}"
            f" | دورکاری: {'بله' if p['remote_ok'] else 'نه'}{' (فقط دورکاری)' if p.get('remote_only') else ''}"
            f" | کنارگذاشته: {', '.join(p.get('exclude_words') or []) or '-'}")
    else:
        out(f"  language: English | roles: {', '.join(p['target_roles'])} | level: {p['seniority']} | places: {', '.join(p['locations']) or 'any'}"
            f" | remote ok: {p['remote_ok']}{' (remote only)' if p.get('remote_only') else ''} | excluded: {', '.join(p.get('exclude_words') or []) or '-'}")


def prefs(a):
    """Show or change preferences without editing JSON by hand. The next report follows them; no re-run needed for ranking changes."""
    ws = P.workspace_path(a.workspace)
    try: p = P.load(ws)
    except FileNotFoundError as e: out(str(e)); return 2
    if a.lang: p["ui_lang"] = a.lang
    if a.add_role: p["target_roles"] += [r for r in a.add_role if r not in p["target_roles"]]
    if a.remove_role: p["target_roles"] = [r for r in p["target_roles"] if r not in a.remove_role]
    if a.seniority: p["seniority"] = a.seniority
    if a.location is not None and a.location: p["locations"] = a.location
    if a.remote is not None: p["remote_ok"] = a.remote == "yes"
    if a.remote_only is not None: p["remote_only"] = a.remote_only == "yes"
    if a.exclude: p["exclude_words"] = list(dict.fromkeys((p.get("exclude_words") or []) + a.exclude))
    if a.unexclude: p["exclude_words"] = [w for w in p.get("exclude_words") or [] if w not in a.unexclude]
    changed = any(x not in (None, [], "") for x in (a.lang, a.add_role, a.remove_role, a.seniority, a.location, a.remote, a.remote_only, a.exclude, a.unexclude))
    if changed:
        P.save(ws, p); out("saved / ذخیره شد")
        if a.add_role: out("new roles need a new search: python -m jobradar run   |   برای عنوان‌های تازه دوباره run بزنید")
        else: out("ranking changes apply at once: python -m jobradar report   |   رتبه‌بندی بلافاصله عوض می‌شود: report")
    show_prefs(p)
    return 0


def links_cmd(a):
    ws = P.workspace_path(a.workspace)
    try: p = P.load(ws)
    except FileNotFoundError as e: out(str(e)); return 2
    fa = p.get("ui_lang") == "fa"
    out("جست‌وجوهایی که خودتان در مرورگر باز می‌کنید:" if fa else "Searches to open in your own browser:")
    for m in LK.manual_links(p):
        out(f"  {m['fa'] if fa else m['en']}")
        for s_ in m["searches"]: out(f"    {s_['role']}: {s_['url']}")
    out("\nصفحهٔ استخدام شرکت‌ها:" if fa else "\nCompany careers pages:")
    for c in LK.companies(): out(f"  {c['name_fa'] if fa else c['name']}: {c['url']}")
    return 0


def run(a):
    ws = P.workspace_path(a.workspace)
    try: p = P.load(ws)
    except FileNotFoundError as e: out(str(e)); return 2
    pr = P.problems(p)
    if pr: [out(x) for x in pr]; return 2
    res = runner.run(ws, p, C.Http(delay=a.delay), sources=a.sources, resume=a.resume, stop_after_units=a.stop_after_units, pages=a.pages, details=a.details, log=out)
    out(f"\nRUN {res['run_id']}: {res['message']}")
    if res["outcome"] in ("succeeded", "partial"):
        out(("قدم بعد" if p.get("ui_lang") == "fa" else "Next step") + ": python -m jobradar report")
    return {"succeeded": 0, "partial": 3, "blocked": 4, "cancelled": 5}[res["outcome"]]


START = {
    "fa": ["رادار شغلی: چند سؤال کوتاه می‌پرسیم، بعد سایت‌های کاریابی را می‌گردیم و یک گزارش فارسی می‌سازیم.",
           "اطلاعات شما فقط روی همین کامپیوتر می‌ماند و هیچ درخواستی خودکار فرستاده نمی‌شود.",
           "۱/۳ پروفایل", "۲/۳ جست‌وجو در کوئرا، ایران‌تلنت و کاربوم (چند دقیقه طول می‌کشد؛ هر وقت خواستید Ctrl+C بزنید، دفعهٔ بعد از همان‌جا ادامه می‌دهد)",
           "۳/۳ گزارش", "پروفایل قبلی پیدا شد؛ همان را به کار می‌بریم. برای تغییر: python -m jobradar prefs",
           "بعداً: «python -m jobradar start» دوباره جست‌وجو می‌کند. برای نشان‌کردن و یادداشت: python -m jobradar serve"],
    "en": ["Job Radar: a few short questions, then we search the job sites and build a report.",
           "Your data stays on this computer and nothing is applied for automatically.",
           "1/3 Profile", "2/3 Searching Quera, IranTalent and Karboom (takes a few minutes; Ctrl+C any time, the next run resumes)",
           "3/3 Report", "Found your existing profile; using it. To change it: python -m jobradar prefs",
           "Later: \"python -m jobradar start\" searches again. To save jobs and add notes: python -m jobradar serve"],
}


def start(a):
    """The guided path for people who do not want to learn commands: profile -> search -> report -> open it."""
    ws = P.workspace_path(a.workspace)
    have = (ws / "profile.json").exists()
    lang = P.load(ws).get("ui_lang", "fa") if have else pick_lang(a)
    m = START[lang]
    out(m[0]); out(m[1]); out(""); out(m[2])
    if have:
        out(m[5]); show_prefs(P.load(ws))
    else:
        if not sys.stdin.isatty():
            out("Run this in a terminal window so it can ask questions, or use: python -m jobradar init --role \"...\""); return 2
        p = wizard(lang); P.save(ws, p); store.conn(ws).close(); show_prefs(p)
        for _, en, fa in P.tips(p): out("💡 " + (fa if lang == "fa" else en))
    p = P.load(ws)
    pr = P.problems(p)
    if pr: [out(x) for x in pr]; return 2
    out(""); out(m[3])
    res = runner.run(ws, p, C.Http(delay=a.delay), resume=True, log=out)
    out(f"   {res['message']}")
    out(""); out(m[4])
    f = RP.write_report(ws); out(f"   {f}")
    if not a.no_open:
        import webbrowser
        try: webbrowser.open(f.resolve().as_uri())
        except Exception: pass
    out(""); out(m[6])
    return 0


def rank_cmd(a):
    ws = P.workspace_path(a.workspace); _, rows = RP.ranked(ws)
    for r in [r for r in rows if r["matched"]][:a.top]:
        out(f'{r["score"]:>4}  {r["title"]} | {r["company"]} | {r["source"]} | {r["key"]}')
        for w in r["why"]: out(f"        - {w}")
    return 0


def report(a):
    f = RP.write_report(P.workspace_path(a.workspace)); out(f"report written: {f}"); return 0


def serve(a):
    srv = RP.serve(P.workspace_path(a.workspace), a.port); out(f"serving http://127.0.0.1:{a.port}/  (Ctrl+C to stop; localhost only)")
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    return 0


def export(a):
    ws = P.workspace_path(a.workspace); txt = RP.export(ws, a.format)
    d = ws / "exports"; d.mkdir(exist_ok=True); f = d / f"jobs.{a.format}"; f.write_text(txt, encoding="utf-8-sig" if a.format == "csv" else "utf-8"); out(f"exported: {f}"); return 0


def mark(a):
    c = store.conn(P.workspace_path(a.workspace))
    store.set_state(c, a.key, a.state); out(f"{a.key} -> {a.state}"); return 0


def note(a):
    c = store.conn(P.workspace_path(a.workspace)); store.set_state(c, a.key, None, a.text); out("note saved"); return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="jobradar"); ap.add_argument("--workspace", "-w", help="workspace folder (default ./workspace or $JOBRADAR_WORKSPACE)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("doctor"); s.add_argument("--offline", action="store_true"); s.set_defaults(f=doctor)
    s = sp.add_parser("init"); s.add_argument("--example", choices=list(P.EXAMPLES)); s.add_argument("--role", action="append", default=[])
    s.add_argument("--seniority", choices=["junior", "mid", "senior"]); s.add_argument("--location", action="append", default=[]); s.add_argument("--name", default="")
    s.add_argument("--force", action="store_true"); s.add_argument("--lang", choices=["fa", "en"], help="interface language (default fa)")
    s.add_argument("--exclude", action="append", default=[], help="hide jobs whose title has this word"); s.add_argument("--remote-only", action="store_true")
    s.add_argument("--no-remote", action="store_true"); s.set_defaults(f=init)
    s = sp.add_parser("prefs", help="show or change preferences")
    s.add_argument("--lang", choices=["fa", "en"]); s.add_argument("--add-role", action="append", default=[]); s.add_argument("--remove-role", action="append", default=[])
    s.add_argument("--seniority", choices=["junior", "mid", "senior"]); s.add_argument("--location", action="append", default=None)
    s.add_argument("--remote", choices=["yes", "no"]); s.add_argument("--remote-only", choices=["yes", "no"])
    s.add_argument("--exclude", action="append", default=[]); s.add_argument("--unexclude", action="append", default=[]); s.set_defaults(f=prefs)
    s = sp.add_parser("start", help="guided: ask, search, report, open (start here)"); s.add_argument("--lang", choices=["fa", "en"])
    s.add_argument("--delay", type=float, default=1.0); s.add_argument("--no-open", action="store_true"); s.set_defaults(f=start)
    sp.add_parser("links", help="search links for JobVision, Jobinja, LinkedIn and company careers pages").set_defaults(f=links_cmd)
    s = sp.add_parser("run"); s.add_argument("--resume", action="store_true"); s.add_argument("--sources", nargs="*", help="quera irantalent karboom")
    s.add_argument("--pages", type=int, default=1); s.add_argument("--details", type=int, default=8, help="detail pages fetched per search"); s.add_argument("--delay", type=float, default=1.0)
    s.add_argument("--stop-after-units", type=int, default=None, help="stop (as if cancelled) after N searches"); s.set_defaults(f=run)
    s = sp.add_parser("rank"); s.add_argument("--top", type=int, default=15); s.set_defaults(f=rank_cmd)
    sp.add_parser("report").set_defaults(f=report)
    s = sp.add_parser("serve"); s.add_argument("--port", type=int, default=8765); s.set_defaults(f=serve)
    s = sp.add_parser("export"); s.add_argument("--format", choices=["csv", "json"], default="csv"); s.set_defaults(f=export)
    s = sp.add_parser("mark"); s.add_argument("key"); s.add_argument("state", choices=["saved", "hidden", "none"]); s.set_defaults(f=mark)
    s = sp.add_parser("note"); s.add_argument("key"); s.add_argument("text"); s.set_defaults(f=note)
    a = ap.parse_args(argv)
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try: sys.stdout.reconfigure(encoding="utf-8")
        except Exception: pass
    return a.f(a)
