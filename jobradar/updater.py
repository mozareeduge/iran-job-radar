"""Check for updates from GitHub releases or tags.
Completely non-blocking, cached, and offline-safe.
"""
import json, time, re, pathlib, urllib.request
from . import __version__

REPO = "mozareeduge/iran-job-radar"
CACHE_TTL = 43200  # 12 hours


def parse_version(v):
    nums = re.findall(r"\d+", str(v))
    return tuple(int(x) for x in nums) if nums else (0, 0, 0)


def is_newer(latest, current):
    return parse_version(latest) > parse_version(current)


def fetch_latest_release(repo=REPO, timeout=2.5):
    """Fetch latest release or tag from GitHub API."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url, headers={"User-Agent": f"iran-job-radar/{__version__}", "Accept": "application/vnd.github.v3+json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                tag = data.get("tag_name", "").lstrip("v")
                html_url = data.get("html_url", f"https://github.com/{repo}")
                return {"version": tag, "url": html_url, "name": data.get("name", tag)}
    except Exception:
        # Fallback to tags if releases is empty
        try:
            t_url = f"https://api.github.com/repos/{repo}/tags"
            t_req = urllib.request.Request(t_url, headers={"User-Agent": f"iran-job-radar/{__version__}", "Accept": "application/vnd.github.v3+json"})
            with urllib.request.urlopen(t_req, timeout=timeout) as resp:
                if resp.status == 200:
                    tags = json.loads(resp.read().decode("utf-8"))
                    if tags and isinstance(tags, list):
                        tag = tags[0].get("name", "").lstrip("v")
                        return {"version": tag, "url": f"https://github.com/{repo}", "name": tag}
        except Exception:
            pass
    return None


def check_update(ws=None, force=False, timeout=2.5):
    """Check for updates, using a cache file in the workspace to avoid unnecessary network queries."""
    cache_file = None
    if ws:
        cache_file = pathlib.Path(ws) / ".update_cache.json"
        if not force and cache_file.exists():
            try:
                cached = json.loads(cache_file.read_text(encoding="utf-8"))
                if time.time() - cached.get("checked_at", 0) < CACHE_TTL:
                    return cached.get("result")
            except Exception:
                pass

    rel = fetch_latest_release(timeout=timeout)
    res = {
        "has_update": False,
        "current_version": __version__,
        "latest_version": __version__,
        "url": f"https://github.com/{REPO}",
        "message_fa": "",
        "message_en": ""
    }

    if rel and rel.get("version"):
        latest = rel["version"]
        res["latest_version"] = latest
        res["url"] = rel.get("url", res["url"])
        if is_newer(latest, __version__):
            res["has_update"] = True
            res["message_fa"] = f"نسخهٔ جدید رادار شغلی ({latest}) منتشر شده است. برای به‌روزرسانی: git pull یا دانلود از گیت‌هاب."
            res["message_en"] = f"A new version of Job Radar ({latest}) is available. To update: git pull or download from GitHub."

    if cache_file:
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps({"checked_at": time.time(), "result": res}, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    return res
