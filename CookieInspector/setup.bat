@echo off
setlocal

echo Installing CookieInspector dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Installing Playwright browsers...
python -m playwright install chromium

echo Setup complete.
pause
