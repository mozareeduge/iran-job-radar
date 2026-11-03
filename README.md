# Iran Job Radar · رادار شغلی ایران

[فارسی](#فارسی) · [English](#english)

<a id="فارسی"></a>
<div dir="rtl">

## فارسی

رادار شغلی ایران یک ابزار سبک، مستقل و متن‌باز است که سایت‌های استخدامی کشور را بر اساس اولویت‌ها، عنوان‌ها و مهارت‌های شما جست‌وجو می‌کند. آگهی‌ها را شفاف رتبه‌بندی می‌کند، در کنار هر امتیاز دلیل دقیق آن را می‌نویسد و نتیجه را در یک گزارش فارسی و راست‌به‌چپ نمایش می‌دهد. 

همه‌چیز ۱۰۰٪ روی رایانهٔ شخصی شما اجرا و ذخیره می‌شود؛ بدون ارسال داده به سرور خارجی، بدون نیاز به ثبت‌نام و بدون ارسال خودکار درخواست همکاری.

### شروع، در سه قدم

۱. **نصب پایتون:** اگر پایتون ندارید، نسخهٔ ۳.۹ به بالا را از [python.org](https://www.python.org/downloads/) نصب کنید (در ویندوز حتماً تیک **Add python to PATH** را بزنید).
۲. **دریافت پروژه:** دکمهٔ سبز **Code** در بالای همین صفحه را بزنید و **Download ZIP** را انتخاب کنید. سپس فایل دانلودشده را از حالت فشرده خارج کنید.
۳. **اجرا:** در ویندوز روی `start.bat` دوبار کلیک کنید. در مک یا لینوکس در ترمینال بزنید: `sh start.sh`

در اجرای اول، چند سؤال کوتاه و مشخص پرسیده می‌شود:
- عنوان‌های شغلی مورد نظر (فارسی و انگلیسی، مثلاً: `کنترل کیفیت, QA engineer`)؛
- سطح تجربه (جونیور، میانی، ارشد)؛
- شهرهای مد نظر (یا خالی برای همهٔ شهرها)؛
- تمایل به دورکاری (بله/خیر و اینکه فقط دورکاری مد نظر است یا خیر)؛
- کلماتی که مایلید از نتایج حذف شوند (مانند فروش، بازاریابی و...)؛
- فایل یا متن رزومه (اختیاری؛ برای تطبیق مهارت‌های تخصصی شما با شرح آگهی‌ها).

سپس رادار منابع را بررسی می‌کند، آگهی‌ها را رتبه‌بندی می‌کند و گزارش را در مرورگر شما باز می‌کند. اگر وسط کار آن را ببندید، در اجرای بعد از همان نقطه کار را ادامه می‌دهد.

---

### منابع و نحوهٔ جست‌وجو

| منبع | نحوهٔ عملکرد | وضعیت و محدودیت‌ها |
|---|---|---|
| [ایران‌تلنت (IranTalent)](https://www.irantalent.com) | خودکار | بررسی دو صفحهٔ اول نتایج برای هر عنوان |
| [کاربوم (Karboom)](https://karboom.io) | خودکار | صفحهٔ اول نتایج و بررسی دقیق تا ۸ آگهی برای هر عنوان |
| [کوئرا مگنت (Quera)](https://quera.org/magnet/jobs) | خودکار | تمرکز روی آگهی‌های فنی و نرم‌افزاری |
| [جاب‌ویژن (JobVision)](https://jobvision.ir) | لینک مستقیم جست‌وجو در گزارش | به‌دلیل شرایط سایت و جلوگیری از انسداد، با یک کلیک در مرورگر خودتان باز می‌شود |
| [جابینجا (Jobinja)](https://jobinja.ir) | لینک مستقیم جست‌وجو در گزارش | همان دلیل |
| [لینکدین (LinkedIn)](https://www.linkedin.com/jobs) | لینک مستقیم جست‌وجو در گزارش | نیاز به ورود به حساب کاربری دارد و برداشت خودکار مجاز نیست |
| [ای‌استخدام (e-estekhdam)](https://www.e-estekhdam.com) | لینک مستقیم جست‌وجو در گزارش | باز شدن مستقیم با فیلترهای شما |
| صفحهٔ استخدام ۱۵ شرکت معتبر | پیوند مستقیم به بخش Careers | دیجی‌کالا، کافه‌بازار، دیوار، تپسی، اسنپ‌فود، باسلام، خودرو۴۵، یکتانت، دیجی‌پی، داتین، سپ، ابر آروان، زرین‌پال، وندار، نماوا |

**اصول فنی:**
- رادار بین درخواست‌ها وقفهٔ ایمن قرار می‌دهد و هرگز سایت‌ها را با ترافیک ناگهانی تحت فشار نمی‌گذارد.
- هرگز وارد حساب‌های کاربری شخصی نمی‌شود و موانع قانونی و لاگین سایت‌ها را دور نمی‌زند.
- اگر دسترسی به منبعی با خطا مواجه شود، در جدول گزارش شفاف با ذکر دلیل ثبت می‌شود تا نتیجهٔ «بدون آگهی» با «خطای دسترسی» اشتباه نشود.

---

### فرمان‌های کاربردی

| کارایی | فرمان |
|---|---|
| اجرای مجدد و سریع جست‌وجو | `python -m jobradar start` |
| ثبت رزومه متنی جهت تطبیق مهارت‌ها | `python -m jobradar resume <path/to/cv.txt>` یا `python -m jobradar resume "متن مهارت‌ها"` |
| ثبت صفحه یا لینکدین | `python -m jobradar linkedin "https://linkedin.com/in/username"` |
| مشاهده مهارت‌های استخراج‌شده | `python -m jobradar resume --show` |
| بررسی انتشار نسخهٔ جدید رادار | `python -m jobradar check-update` |
| پنل مدیریت، نشان‌کردن و یادداشت در مرورگر | `python -m jobradar serve` (باز کردن http://127.0.0.1:8765) |
| تغییر سریع تنظیمات | `python -m jobradar prefs --add-role "تحلیلگر داده" --remote-only yes --exclude فروش` |
| تغییر زبان گزارش (فارسی / انگلیسی) | `python -m jobradar prefs --lang fa` یا `--lang en` |
| دریافت لینک‌های دستی برای مرورگر | `python -m jobradar links` |
| خروجی اکسل و داده‌ها | `python -m jobradar export > jobs.csv` |
| بررسی سلامت سیستم و منابع | `python -m jobradar doctor` |

</div>


---

<a id="english"></a>

## English

Iran Job Radar is a lightweight, local-first open-source tool that searches major Iranian job boards and companies according to your target roles and skills. It transparently ranks job listings, explains every point gained or lost, and renders an offline Persian (RTL) or English report.

Everything stays strictly on your machine — no third-party cloud uploads, no logins required, and no automatic applications.

### Quickstart

1. **Install Python:** Ensure Python 3.9+ is installed (tick **Add python to PATH** on Windows).
2. **Download:** Click the green **Code** button above → **Download ZIP**, then extract it.
3. **Run:** Double-click `start.bat` on Windows, or run `sh start.sh` on macOS/Linux.

On first run, it guides you through a few quick questions:
- Target job titles (e.g. `QA engineer, کنترل کیفیت`);
- Seniority level (junior, mid, senior);
- Preferred cities (or blank for anywhere);
- Remote preference (allowed, or remote-only);
- Excluded keywords (e.g. sales, marketing);
- Optional resume file or text summary (to match technical skills against job descriptions).

It searches the sources, ranks the results with plain-language explanations, and opens the HTML report in your browser. Subsequent runs resume from where you left off.

---

### Sources & Coverage

| Source | Mode | Notes |
|---|---|---|
| [IranTalent](https://www.irantalent.com) | Automated | First 2 result pages per role |
| [Karboom](https://karboom.io) | Automated | First page and full details for top 8 ads per role |
| [Quera Magnet](https://quera.org/magnet/jobs) | Automated | Primarily software engineering & technical roles |
| [JobVision](https://jobvision.ir) | Direct search link | Terms restrict scraping; opens pre-filtered in your browser |
| [Jobinja](https://jobinja.ir) | Direct search link | Same reason |
| [LinkedIn](https://www.linkedin.com/jobs) | Direct search link | Login wall & automated scraping forbidden |
| [e-estekhdam](https://www.e-estekhdam.com) | Direct search link | Direct pre-filtered link |
| 15 Iranian Tech Careers Pages | Direct links in report | Digikala, Cafe Bazaar, Divar, Tapsi, Snappfood, Basalam, Khodro45, Yektanet, Digipay, Dotin, SEP, ArvanCloud, ZarinPal, Vandar, Namava |

---

### Useful Commands

| Task | Command |
|---|---|
| Run search & open report | `python -m jobradar start` |
| Add resume / skills for matching | `python -m jobradar resume <file.txt>` or `python -m jobradar resume "skills list"` |
| Set LinkedIn profile URL | `python -m jobradar linkedin "https://linkedin.com/in/username"` |
| View current resume skills | `python -m jobradar resume --show` |
| Check for new releases on GitHub | `python -m jobradar check-update` |
| Interactive local browser panel | `python -m jobradar serve` (open http://127.0.0.1:8765) |
| Change preferences without editing files | `python -m jobradar prefs --add-role "data analyst" --remote-only yes --exclude sales` |
| Change interface language | `python -m jobradar prefs --lang en` or `--lang fa` |
| Export to CSV / JSON | `python -m jobradar export > jobs.csv` |
| Check system and site reachability | `python -m jobradar doctor` |

---

### Transparent Ranking Logic

Every listing begins at 0 points and gains or loses points with explicit reasons:

| Criterion | Points |
|---|---|
| Title exactly matches a target role | +40 |
| Title contains all words of a target role | +28 |
| Title shares a significant word with a target role | +12 |
| Job description mentions a target role | +8 |
| Target role absent from title and description | −20 |
| Job description matches skills from your resume/LinkedIn | +3 per skill (up to +15 max) |
| Seniority matches your level | +12 |
| Seniority differs by one tier | −4 |
| Seniority differs by two tiers | −15 |
| Remote job, and you accept remote | +10 |
| Location matches your city list | +8 |
| Location differs from your city list | −6 |
| You requested remote-only, but job is on-site | −25 |
| You requested remote-only, but job is hybrid | −10 |
| Posted within the last 7 days | +5 |
| Older than 90 days | −5 |
| Job is expired / closed | −30 |

Duplicate listings across different portals are merged into a single card linking to all sources. Listings containing your excluded words are cleanly separated into a hidden section with reasons shown. Full details in [`jobradar/rank.py`](jobradar/rank.py).

---

### For Agents and Automation

Commands run completely headless and scriptable:

```bash
python -m jobradar init --lang fa --role "توسعه‌دهنده پایتون" --role "backend developer" --seniority senior --location Tehran
python -m jobradar resume "Python, FastAPI, Docker, PostgreSQL, Redis, Kafka"
python -m jobradar run --sources irantalent,karboom
python -m jobradar report
```

Exit codes:
- `0`: Succeeded
- `3`: Partial (some sources temporarily blocked or unreachable; others succeeded)
- `4`: Blocked
- `5`: Cancelled

Run tests: `pytest -q`

---

### Privacy & Security

Your profile, resume text, notes, and scraped results live exclusively in `workspace/` on your computer. Nothing is transmitted externally. See [SECURITY.md](SECURITY.md).

### Licence

[MIT](LICENSE). Job listings remain the intellectual property of their respective publishers.
