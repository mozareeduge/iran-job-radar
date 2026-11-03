#!/usr/bin/env sh
# Job Radar: guided start for macOS and Linux.
cd "$(dirname "$0")" || exit 1
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is not installed: https://www.python.org/downloads/  |  پایتون ۳ نصب نیست"; exit 1; }
if [ ! -x .venv/bin/python ]; then
  echo "Preparing, once only... / آماده‌سازی، فقط بار اول..."
  python3 -m venv .venv && .venv/bin/python -m pip install -q -r requirements.txt || { echo "Could not install packages. Check your internet. / نصب نشد؛ اینترنت را بررسی کنید."; exit 1; }
fi
exec .venv/bin/python -m jobradar start "$@"
