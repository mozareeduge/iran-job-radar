"""Source adapters for Quera Magnet, IranTalent and Karboom: the public search pages and endpoints a browser uses.
Every failure becomes a named Blocked reason, so a run never fails silently.
JobVision and Jobinja are not read automatically (their terms restrict it); `jobradar links` gives search links instead."""
import re, json, html, time, datetime as dt
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"}
DISABLED = {"jobvision": "not read automatically: site terms restrict automated collection; use `jobradar links`", "jobinja": "not read automatically: site terms restrict automated collection; use `jobradar links`"}
NEXT = re.compile(r'__NEXT_DATA__[^>]*>(.*?)</script>', re.S)
LOGIN = re.compile(r'(type=["\']password["\']|name=["\']password["\']|<form[^>]+action=["\'][^"\']*login)', re.I)   # a real login form, not a nav link
MODES = [("remote", r"(دورکاری|دور\s*کاری|fully\s*remote|remote[- ]first|remote\s*(work|position|role|job)|work\s*from\s*home)"),
         ("hybrid", r"(hybrid|هیبرید|نیمه\s*حضوری)"), ("onsite", r"(on[- ]?site|in[- ]office|کاملا\s*حضوری|حضور\s*در\s*محل)")]
PART = re.compile(r"(part[- ]?time|پاره\s*وقت|پارت\s*تایم)", re.I)


class Rows(list):
    """Rows found by one search, plus how many were skipped because they are already stored (still counted as found)."""
    seen = 0


class Blocked(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class Http:
    """Polite requests wrapper: one request at a time, delay between calls. System proxy ignored unless JOBRADAR_USE_PROXY=1."""
    def __init__(self, delay=1.0, timeout=25):
        import requests, os
        self.s = requests.Session()
        self.s.headers.update(UA)
        self.s.trust_env = os.environ.get("JOBRADAR_USE_PROXY") == "1"
        self.delay, self.timeout, self._last = delay, timeout, 0.0

    def _wait(self):
        w = self.delay - (time.time() - self._last)
        if w > 0:
            time.sleep(w)
        self._last = time.time()

    def get(self, url, **kw):
        self._wait()
        return self.s.get(url, timeout=self.timeout, **kw)

    def post(self, url, **kw):
        self._wait()
        return self.s.post(url, timeout=self.timeout, **kw)


def clean(h):
    if not h:
        return ""
    t = BeautifulSoup(html.unescape(h), "html.parser").get_text("\n")
    return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t‏‎]+", " ", t)).strip()


def call(fn, *a, **k):
    try:
        r = fn(*a, **k)
    except Exception as e:
        raise Blocked(f"network error: {type(e).__name__}")
    c = r.status_code
    if c in (401, 403):
        raise Blocked(f"http {c} (access refused)")
    if c == 429:
        raise Blocked("http 429 (rate limited)")
    if c >= 500:
        raise Blocked(f"http {c} (source down)")
    if c >= 400:
        raise Blocked(f"http {c}")
    return r


def wall_or_format(text):
    return Blocked("login wall" if LOGIN.search(text or "") else "unexpected page format")


def norm_row(**d):
    base = dict(source="", source_id="", url="", title="", company="", location="", work_mode="unknown", employment="", seniority="",
                salary="", posted_at="", expires_at="", live=None, jd="")
    base.update(d)
    txt = f'{base["title"]}\n{base["jd"][:2000]}'
    if base["work_mode"] in ("", "unknown"):
        f = [m for m, p in MODES if re.search(p, txt, re.I)]
        base["work_mode"] = "hybrid" if "hybrid" in f else (f[0] if f else "unknown")
    if PART.search(f'{base["employment"]} {base["title"]}'):
        base["employment"] = "part-time"
    return base


# ---- Quera Magnet (Next.js page data) ----
def quera_unit(http, kw, pages=1, details=8, known=()):
    r = call(http.get, "https://quera.org/magnet/jobs", params={"search": kw})
    m = NEXT.search(r.text)
    if not m:
        raise wall_or_format(r.text)
    try:
        edges = json.loads(m.group(1))["props"]["pageProps"]["jobs"]["edges"]
    except Exception:
        raise Blocked("unexpected page format")
    rows, fetched = [], 0
    for e in edges:
        n = e.get("node") or {}
        pk = n.get("pk")
        if not pk:
            continue
        city = n.get("city")
        row = norm_row(source="Quera Magnet", source_id=f"qm-{pk}", url=f"https://quera.org/magnet/jobs/{pk}", title=n.get("title", ""),
                       company=(n.get("company") or {}).get("name", "") if isinstance(n.get("company"), dict) else "",
                       location=city.get("name", "") if isinstance(city, dict) else "",
                       work_mode="remote" if n.get("offers_remote") else "unknown", employment=n.get("collaboration_type", "") or "",
                       seniority=n.get("level", "") or "", salary=n.get("salary_short") or "", live=n.get("open", True))
        if f"Quera Magnet:qm-{pk}" not in known and fetched < details:
            fetched += 1
            try:
                dr = call(http.get, row["url"])
                j = json.loads(NEXT.search(dr.text).group(1))["props"]["pageProps"]["job"]
                sch = json.loads(j.get("schema") or "{}")
                row.update(company=(j.get("company") or {}).get("name", "") or row["company"],
                           location=((j.get("city") or {}).get("name") or row["location"]),
                           jd=clean(sch.get("description") or j.get("description_summary") or ""), posted_at=(sch.get("datePosted") or "")[:10],
                           expires_at=(sch.get("validThrough") or "")[:10], live=bool(j.get("open", True)),
                           employment=j.get("collaboration_type", "") or row["employment"], salary=j.get("salary_short") or j.get("salary") or row["salary"])
                row = norm_row(**row)
            except Exception:
                pass  # detail is optional; the list row is still a real observation
        rows.append(row)
    return rows


# ---- IranTalent (JSON search API) ----
def irantalent_unit(http, kw, pages=2, details=0, known=()):
    H = {"Origin": "https://www.irantalent.com", "Referer": "https://www.irantalent.com/"}
    rows = []
    for p in range(1, pages + 1):
        r = call(http.post, f"https://api.irantalent.com/api/v1/employer/position/search-by-slug?sort_by=lived_at&page={p}",
                 headers=H, json={"keyword": kw, "is_job_page": False})
        try:
            d = r.json()["data"]
        except Exception:
            raise wall_or_format(r.text)
        for j in d.get("data", []):
            bd = j.get("brand_data") or {}
            emp = j.get("employment_type") or {}
            st = j.get("status") or {}
            sal = f"{j.get('salary_from') or ''}-{j.get('salary_to') or ''}" if j.get("is_show_salary") and (j.get("salary_from") or j.get("salary_to")) else ""
            rows.append(norm_row(
                source="IranTalent", source_id=f"it-{j['id']}", url=f"https://www.irantalent.com/job/{j.get('slug', 'x')}/{j['id']}",
                title=j.get("title") or j.get("title_farsi") or "", company=bd.get("name_fa") or bd.get("name_en") or "",
                location=j.get("location_text_farsi") or "",
                work_mode={"on_site": "onsite", "remote": "remote", "hybrid": "hybrid"}.get(j.get("work_type"), "unknown"),
                employment=emp.get("title", "") if isinstance(emp, dict) else "",
                seniority=", ".join(s.get("title", "") for s in j.get("seniority") or []),
                salary=sal, posted_at=(j.get("lived_at") or j.get("created_at") or "")[:10], expires_at=(j.get("expired_at") or "")[:10],
                live=(j.get("expired_at") is None) and str(st.get("slug", st.get("title", "active"))).lower() not in ("expired", "closed"),
                jd=clean((j.get("role_description") or "") + "\n" + (j.get("role_description_farsi") or ""))))
        if p >= (d.get("last_page") or 1):
            break
    return rows


# ---- Karboom (HTML list + JSON-LD detail) ----
def karboom_unit(http, kw, pages=1, details=8, known=()):
    links = []
    for p in range(1, pages + 1):
        r = call(http.get, "https://karboom.io/jobs", params={"q": kw, "page": p})
        found = list(dict.fromkeys(re.findall(r'href="(https://karboom\.io/jobs/[a-z0-9]{5,8}/[^"]+)"', r.text)))
        if not found:
            if p == 1 and LOGIN.search(r.text):
                raise wall_or_format(r.text)
            break
        links += [u for u in found if u not in links]
    rows = Rows()
    for u in links[:max(details, 0)]:
        sid = "kb-" + u.split("/")[4]
        if f"Karboom:{sid}" in known:
            rows.seen += 1
            continue
        try:
            r = call(http.get, u)
        except Blocked as e:
            if "refused" in e.reason or "rate" in e.reason:
                raise
            continue
        s = BeautifulSoup(r.text, "html.parser")
        jp = {}
        for sc in s.select('script[type="application/ld+json"]'):
            if '"JobPosting"' in (sc.string or ""):
                try:
                    jp = json.loads(sc.string, strict=False)
                except Exception:
                    jp = {"title": (re.search(r'"title"\s*:\s*"([^"]*)"', sc.string) or [None, ""])[1]}
        if isinstance(jp, list):
            jp = next((x for x in jp if isinstance(x, dict)), {})
        h1 = s.select_one("h1")
        t = jp.get("title") or (h1.get_text(" ", strip=True) if h1 else "")
        if not t:
            continue
        body = s.select_one(".job-description, .description, article") or s
        org = jp.get("hiringOrganization") or {}
        vt = (jp.get("validThrough") or "")[:10]
        rows.append(norm_row(source="Karboom", source_id=sid, url=u, title=t, company=org.get("name", "") if isinstance(org, dict) else "",
                             posted_at=(jp.get("datePosted") or "")[:10], expires_at=vt, jd=clean(str(body))[:6000],
                             live=(not vt or vt >= dt.date.today().isoformat())))
    return rows


UNITS = {"quera": quera_unit, "irantalent": irantalent_unit, "karboom": karboom_unit}
NAMES = {"quera": "Quera Magnet", "irantalent": "IranTalent", "karboom": "Karboom"}
