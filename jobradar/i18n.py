"""Two interface languages: Persian (fa, right-to-left) and English (en). Job text is never translated; it is shown as published."""

T = {
    "fa": {
        "title": "رادار شغلی",
        "profile": "پروفایل", "roles": "عنوان‌ها", "level": "سطح", "places": "شهرها", "remote_ok": "دورکاری قبول است",
        "yes": "بله", "no": "نه", "any": "هر جا", "unnamed": "بی‌نام",
        "last_run": "آخرین جست‌وجو", "at": "در",
        "no_run": "هنوز جست‌وجویی تمام نشده. قدم بعد: <code dir=\"ltr\">python -m jobradar run</code>",
        "coverage": "کجا را گشتیم و کجا را نه",
        "c_source": "منبع", "c_tried": "جست‌وجوهای انجام‌شده", "c_ok": "موفق", "c_blocked": "مسدود / توضیح", "c_jobs": "آگهی", "c_last": "آخرین موفقیت",
        "scope": "دامنه: فقط آگهی‌هایی که از داخل ایران می‌شود برایشان درخواست داد. پاره‌وقت و تمام‌وقت یکسان رتبه می‌گیرند. کنار هر امتیاز دلیلش آمده است و هیچ درخواستی خودکار فرستاده نمی‌شود.",
        "saved": "نشان‌شده‌ها", "ranked": "رتبه‌بندی‌شده", "shown": "مورد نمایش داده شد", "hidden": "پنهان‌شده‌ها",
        "none_match": "هنوز آگهی‌ای با عنوان‌های شما پیدا نشد. عنوان‌های بیشتری (فارسی و انگلیسی) به پروفایل اضافه کنید یا جدول بالا را ببینید.",
        "unmatched": "آگهی دیگر جمع شد که هیچ‌کدام از عنوان‌های شما در آن نبود؛ این‌ها نمایش داده نمی‌شوند ولی در خروجی CSV هستند.",
        "static": "این گزارش ثابت است. برای نشان‌کردن، پنهان‌کردن یا یادداشت: <code dir=\"ltr\">python -m jobradar serve</code>",
        "save": "نشان کن", "hide": "پنهان کن", "clear": "پاک کن", "note": "یادداشت", "note_ph": "یادداشت شما (فقط روی همین کامپیوتر می‌ماند)",
        "also_on": "نسخه‌های دیگر همین آگهی:", "never": "هرگز", "save_failed": "ذخیره نشد",
        "manual": "این‌ها را خودتان باز کنید (رادار آن‌ها را نمی‌خواند)",
        "manual_why": "جاب‌ویژن، جابینجا و لینکدین را رادار خودکار نمی‌خواند، چون قوانین این سایت‌ها برداشت خودکار را محدود می‌کند یا دسترسی را می‌بندند. لینک‌های زیر همان جست‌وجو را با عنوان‌های شما در مرورگر خودتان باز می‌کنند.",
        "companies": "صفحهٔ استخدام شرکت‌ها",
        "companies_why": "این صفحه‌ها در تاریخ بررسی باز می‌شدند. رادار آن‌ها را نمی‌خواند؛ برای سر زدن دستی است. فهرست در <code dir=\"ltr\">jobradar/data/companies.json</code> است و می‌توانید شرکت اضافه کنید.",
        "checked": "بررسی‌شده در",
        "outcome": {"succeeded": "کامل", "partial": "ناقص", "blocked": "مسدود", "cancelled": "نیمه‌کاره", "running": "در حال اجرا"},
        "why_head": "چرا این رتبه",
        "excluded": "پنهان شد چون کلمهٔ کنارگذاشته‌شدهٔ شما را دارد",
        "disabled": "خاموش (قوانین سایت)",
        "resume_skills": "مهارت‌های رزومه",
        "skills_found": "مهارت تطبیق داده شد",
        "update_available": "نسخهٔ جدید موجود است",
    },
    "en": {
        "title": "Job Radar",
        "profile": "Profile", "roles": "roles", "level": "level", "places": "places", "remote_ok": "remote ok",
        "yes": "yes", "no": "no", "any": "any", "unnamed": "unnamed",
        "last_run": "Last run", "at": "at",
        "no_run": "<b>No finished run yet.</b> Next step: <code>python -m jobradar run</code>",
        "coverage": "Coverage (what was and was not looked at)",
        "c_source": "Source", "c_tried": "Searches tried", "c_ok": "Succeeded", "c_blocked": "Blocked / note", "c_jobs": "Jobs", "c_last": "Last success",
        "scope": "Scope: roles an Iran-based person can apply for. Part-time and full-time are ranked the same. Scores are shown with reasons; nothing is auto-applied.",
        "saved": "Saved", "ranked": "Ranked", "shown": "shown", "hidden": "Hidden",
        "none_match": "No jobs match your roles yet. Add more titles (Persian and English) to your profile, or check the coverage table above.",
        "unmatched": "more collected jobs did not mention any of your target roles and are not shown (they are in the export).",
        "static": "Static report. To save, hide or add notes: <code>python -m jobradar serve</code> (or <code>jobradar mark KEY saved|hidden</code>).",
        "save": "Save", "hide": "Hide", "clear": "Clear", "note": "Note", "note_ph": "your note (stays on this computer)",
        "also_on": "other copies:", "never": "never", "save_failed": "save failed",
        "manual": "Open these yourself (the radar does not read them)",
        "manual_why": "JobVision, Jobinja and LinkedIn are not read automatically: their terms restrict automated collection or they refuse access. These links open the same search, with your titles, in your own browser.",
        "companies": "Company careers pages",
        "companies_why": "These pages opened on the check date. The radar does not read them; they are for visiting by hand. The list is <code>jobradar/data/companies.json</code>; add your own.",
        "checked": "checked",
        "outcome": {"succeeded": "succeeded", "partial": "partial", "blocked": "blocked", "cancelled": "cancelled", "running": "running"},
        "why_head": "why this rank",
        "excluded": "hidden because it contains one of your excluded words",
        "disabled": "off (site terms)",
        "resume_skills": "resume skills",
        "skills_found": "skills matched",
        "update_available": "New version available",
    },
}

CLI = {
    "fa": {
        "next": "قدم بعد", "ready": "پوشهٔ کار آماده شد", "profile_saved": "پروفایل ذخیره شد",
        "report_written": "گزارش ساخته شد", "open_it": "این فایل را در مرورگر باز کنید",
        "serving": "باز کنید: http://127.0.0.1:{port}/  (برای توقف Ctrl+C؛ فقط روی همین کامپیوتر)",
    },
    "en": {
        "next": "Next step", "ready": "workspace ready", "profile_saved": "profile saved",
        "report_written": "report written", "open_it": "open this file in your browser",
        "serving": "serving http://127.0.0.1:{port}/  (Ctrl+C to stop; localhost only)",
    },
}

# What each block reason means, in plain words, for a person who is not technical.
REASON_FA = {
    "http 403": "سایت دسترسی را بست (۴۰۳)",
    "http 429": "سایت گفت درخواست زیاد است؛ کمی بعد دوباره امتحان کنید",
    "login wall": "سایت ورود به حساب می‌خواهد؛ رادار هرگز وارد حساب نمی‌شود",
    "network error": "اتصال برقرار نشد (اینترنت، فیلتر یا قطعی سایت)",
    "unexpected page format": "شکل صفحه عوض شده؛ احتمالاً نیاز به به‌روزرسانی رادار",
    "source down": "سایت در دسترس نبود",
}


def t(lang):
    return T.get(lang) or T["fa"]


def c(lang):
    return CLI.get(lang) or CLI["en"]


def reason(lang, text):
    if lang != "fa":
        return text
    for k, v in REASON_FA.items():
        if k in text:
            return f"{v} ({text})"
    return text


FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def num(lang, n):
    s = str(n)
    return s.translate(FA_DIGITS) if lang == "fa" else s


def when(iso_str):
    if not iso_str:
        return "-"
    return iso_str[:16].replace("T", " ")


EMP_FA = {"full-time": "تمام‌وقت", "part-time": "پاره‌وقت", "contract": "قراردادی", "internship": "کارآموزی"}


def emp(lang, val):
    val = (val or "").strip().lower()
    if lang == "fa":
        return EMP_FA.get(val, val)
    return val
