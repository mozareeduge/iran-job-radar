@echo off
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul || (echo Python is not installed. Install it from https://www.python.org/downloads/ and tick "Add python to PATH". & echo پایتون نصب نیست. از python.org نصب کنید و گزینهٔ Add python to PATH را بزنید. & pause & exit /b 1)
if not exist .venv\Scripts\python.exe (
  echo Preparing, once only... / آماده‌سازی، فقط بار اول...
  python -m venv .venv || (pause & exit /b 1)
  .venv\Scripts\python.exe -m pip install -q -r requirements.txt || (echo Could not install packages. Check your internet. / نصب نشد؛ اینترنت را بررسی کنید. & pause & exit /b 1)
)
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe -m jobradar start
pause
