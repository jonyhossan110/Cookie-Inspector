#!/usr/bin/env bash
set -e

echo "Installing CookieInspector dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Installing Playwright browsers..."
python3 -m playwright install chromium

echo "Setup complete."
