# Iran Job Radar · رادار شغلی ایران

[فارسی](#فارسی) · [English](#english)

<a id="فارسی"></a>
<div dir="rtl">

## فارسی

رادار شغلی چند سایت کاریابی ایرانی را با عنوان‌های شغلی شما می‌گردد. آگهی‌ها را برای شما رتبه‌بندی می‌کند و کنار هر امتیاز دلیلش را می‌نویسد. نتیجه یک گزارش فارسی و راست‌به‌چپ است. همه‌چیز روی کامپیوتر خود شما می‌ماند و هیچ درخواستی خودکار فرستاده نمی‌شود.

### شروع، در سه قدم

۱. [پایتون](https://www.python.org/downloads/) را نصب کنید. در ویندوز تیک **Add python to PATH** را بزنید.

۲. همین صفحه را دانلود کنید: دکمهٔ سبز **Code** و بعد **Download ZIP**. فایل را از حالت فشرده خارج کنید.

۳. در ویندوز روی `start.bat` دوبار کلیک کنید. در مک یا لینوکس این را بزنید: `sh start.sh`

رادار اول زبان را می‌پرسد (فارسی یا English). بعد این چند سؤال کوتاه را می‌پرسد:

- چه شغلی می‌خواهید؛
- سطحتان چیست؛
- کدام شهرها برایتان مناسب است؛
- دورکاری را قبول دارید یا نه؛
- چه کلمه‌هایی نباید در عنوان آگهی باشد.

بعد جست‌وجو می‌کند، گزارش می‌سازد و آن را در مرورگر باز می‌کند. بار اول چند دقیقه طول می‌کشد. اگر وسط کار ببندید، دفعهٔ بعد از همان‌جا ادامه می‌دهد.

**راهنما:** عنوان‌ها را هم فارسی بنویسید هم انگلیسی، مثلاً «کنترل کیفیت, QA engineer». خیلی از آگهی‌ها فقط به یکی از این دو زبان نوشته می‌شوند. اگر فقط یکی را بنویسید، رادار خودش یادآوری می‌کند.

### کجا را می‌گردد

| سایت | چطور | محدودیت |
|---|---|---|
| [ایران‌تلنت](https://www.irantalent.com) | خودکار | دو صفحهٔ اول نتایج برای هر عنوان |
| [کاربوم](https://karboom.io) | خودکار | صفحهٔ اول نتایج و جزئیات حداکثر ۸ آگهی برای هر عنوان |
| [کوئرا مگنت](https://quera.org/magnet/jobs) | خودکار | بیشتر آگهی‌های برنامه‌نویسی و فنی؛ برای شغل‌های دیگر معمولاً خالی است |
| [جاب‌ویژن](https://jobvision.ir) | لینک جست‌وجو در گزارش | قوانین سایت برداشت خودکار را محدود می‌کند؛ شما در مرورگر خودتان باز می‌کنید |
| [جابینجا](https://jobinja.ir) | لینک جست‌وجو در گزارش | همان دلیل |
| [لینکدین](https://www.linkedin.com/jobs) | لینک جست‌وجو در گزارش | ورود به حساب لازم است و برداشت خودکار ممنوع است |
| [ای‌استخدام](https://www.e-estekhdam.com) | لینک جست‌وجو در گزارش | — |
| صفحهٔ استخدام ۱۵ شرکت ایرانی | فهرست لینک در گزارش | دیجی‌کالا، کافه‌بازار، دیوار، تپسی، اسنپ‌فود، باسلام، خودرو۴۵، یکتانت، دیجی‌پی، داتین، سپ، ابر آروان، زرین‌پال، وندار، نماوا. همه در ۱۲ آبان ۱۴۰۵ بررسی شدند و باز می‌شدند. |

قاعده‌ها:

- رادار هر بار فقط یک صفحه می‌خواهد و بین درخواست‌ها یک ثانیه صبر می‌کند.
- هرگز وارد حساب کاربری نمی‌شود و هرگز مسدودیت سایت‌ها را دور نمی‌زند.
- اگر سایتی جواب ندهد، گزارش اسم آن سایت و دلیلش را می‌نویسد. پس «هیچ آگهی‌ای نبود» با «نتوانستیم بگردیم» اشتباه گرفته نمی‌شود.

### بعد از اولین گزارش

| کار | فرمان |
|---|---|
| دوباره گشتن | `python -m jobradar start` |
| نشان‌کردن، پنهان‌کردن و یادداشت در مرورگر | `python -m jobradar serve` و بعد باز کردن http://127.0.0.1:8765 |
| تغییر سلیقه بدون دست‌زدن به فایل | `python -m jobradar prefs --add-role "تحلیلگر داده" --remote-only yes --exclude فروش` |
| عوض کردن زبان گزارش | `python -m jobradar prefs --lang en` یا `--lang fa` |
| لینک جاب‌ویژن، جابینجا، لینکدین و شرکت‌ها | `python -m jobradar links` |
| خروجی اکسل (CSV) | `python -m jobradar export > jobs.csv` |
| بررسی اتصال سایت‌ها | `python -m jobradar doctor` |

تغییر سطح، شهر، دورکاری یا کلمه‌های کنارگذاشته رتبه‌بندی را فوراً عوض می‌کند. عنوان شغلی تازه به یک جست‌وجوی تازه نیاز دارد.

</div>

<a id="english"></a>

## English

Job Radar searches several Iranian job sites using your job titles. It ranks the ads for you and shows the reason next to each score. You get a report in Persian (right-to-left) or English. Everything stays on your computer, and it never applies to a job for you.

### Start in three steps

1. Install [Python](https://www.python.org/downloads/). On Windows, tick **Add python to PATH**.
2. Download this repo: green **Code** button → **Download ZIP**, then unzip it.
3. On Windows, double-click `start.bat`. On macOS or Linux, run `sh start.sh`.

It asks for your language first, then a few short questions:

- which jobs you want;
- your level;
- which cities work for you;
- whether remote is OK;
- which words should not appear in a job title.

It then searches, builds the report and opens it in your browser. The first run takes a few minutes. If you stop it, the next run carries on from where it stopped.

**Tip:** give titles in both Persian and English, e.g. `QA engineer, کنترل کیفیت`. Many ads are written in only one of the two. If you give only one, the radar reminds you.

### Where it searches

| Site | How | Limit |
|---|---|---|
| [IranTalent](https://www.irantalent.com) | automatic | first 2 result pages per title |
| [Karboom](https://karboom.io) | automatic | first result page, details for up to 8 ads per title |
| [Quera Magnet](https://quera.org/magnet/jobs) | automatic | mostly programming and tech jobs; usually empty for other fields |
| [JobVision](https://jobvision.ir) | search link in the report | its terms restrict automated collection; you open it in your own browser |
| [Jobinja](https://jobinja.ir) | search link in the report | same reason |
| [LinkedIn](https://www.linkedin.com/jobs) | search link in the report | needs a login and forbids automated collection |
| [e-estekhdam](https://www.e-estekhdam.com) | search link in the report | — |
| Careers pages of 15 Iranian companies | link list in the report | Digikala, Cafe Bazaar, Divar, Tapsi, Snappfood, Basalam, Khodro45, Yektanet, Digipay, Dotin, SEP, ArvanCloud, ZarinPal, Vandar, Namava. Each one opened when checked on 3 Nov 2026. List: [`jobradar/data/companies.json`](jobradar/data/companies.json). |

Rules:

- The radar asks for one page at a time and waits one second between requests.
- It never logs in to a site and never gets around a block.
- When a site fails, the report names the site and gives the reason. That way "no jobs" is never confused with "could not search".

### After the first report

| Task | Command |
|---|---|
| Search again | `python -m jobradar start` |
| Save, hide and add notes in the browser | `python -m jobradar serve`, then open http://127.0.0.1:8765 |
| Change preferences without editing files | `python -m jobradar prefs --add-role "data analyst" --remote-only yes --exclude sales` |
| Change the report language | `python -m jobradar prefs --lang fa` or `--lang en` |
| Get JobVision, Jobinja, LinkedIn and company links | `python -m jobradar links` |
| Export to a spreadsheet (CSV) | `python -m jobradar export > jobs.csv` |
| Check whether the sites are reachable | `python -m jobradar doctor` |

Changing your level, cities, remote setting or excluded words re-ranks the results at once. A new job title needs a new search.

### How the ranking works

Each job starts at 0 points. It gains or loses points in these ways:

| Rule | Points |
|---|---|
| Title matches one of your roles | +40 |
| Title has all the words of a role | +28 |
| Title shares a word with a role | +12 |
| Description mentions a role | +8 |
| No role found anywhere | −20 |
| Level matches yours | +12 |
| Level one step away | −4 |
| Level two steps away | −15 |
| Remote, and you accept remote | +10 |
| Your city | +8 |
| Another city | −6 |
| You want remote only, and the job is on-site | −25 |
| You want remote only, and the job is hybrid | −10 |
| Ad language not in your list | −8 |
| Posted in the last week | +5 |
| Older than 90 days | −5 |
| Ad is closed | −30 |

Full-time and part-time jobs are ranked the same. If the same job appears on two sites, it is merged into one card that links to both. Jobs with one of your excluded words are hidden, and the hidden list shows why. The rules are in [`jobradar/rank.py`](jobradar/rank.py).

### For agents and scripts

Everything also runs without prompts:

```
python -m jobradar init --lang en --role "qa engineer" --role "کنترل کیفیت" --seniority junior --location Tehran
python -m jobradar run --sources irantalent,karboom
```

Exit codes from `run`:

| Code | Meaning |
|---|---|
| 0 | succeeded |
| 3 | partial (some sources failed; they are named) |
| 4 | blocked |
| 5 | cancelled |

Tests: `pip install pytest && python -m pytest -q`

### Privacy

Your profile, the jobs found, your notes and your marks stay in `workspace/` on your computer. Nothing is uploaded. See [SECURITY.md](SECURITY.md).

### Licence

[MIT](LICENSE). Job ads belong to their publishers. The radar shows the title and a link and sends you to the original page.
