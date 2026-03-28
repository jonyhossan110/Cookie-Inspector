# JS-Leaker

**JavaScript Secret Scanner and Link Collector**

- Author: **Md. Jony Hassain**
- GitHub: https://github.com/jonyhossan110/JS-Leaker

JS-Leaker is a professional security utility for discovering and analyzing JavaScript-based information leaks. It crawls a target web page, collects external and inline JavaScript assets, scans code for credential patterns (API keys, tokens, secrets), and writes structured reports into an `output/` directory.

## ✅ Features

- Crawl and extract JavaScript references from websites
- Download external JS files and parse inline scripts
- Keyword- and regex-based secret detection (JWT, API keys, tokens, passwords)
- Multi-threaded processing (configurable worker threads)
- Supports CSV and plain text report outputs
- Minimal dependencies, portable across Windows and Linux

## 📌 Prerequisites (global)

- Python 3.x (3.8+ recommended)

## 🐧 Prerequisites (Kali Linux)

Kali Linux requires development dependencies for building Python extension packages.

- `build-essential`
- `python3-dev`
- `python3-venv`

```bash
sudo apt update
sudo apt install python3-pip python3-venv build-essential python3-dev -y
```

## 🛠 Setup Roadmap for Windows

1. Clone repository:

```powershell
git clone https://github.com/jonyhossan110/JS-Leaker.git
cd JS-Leaker
```

2. Create and activate virtual environment:

```powershell
python -m venv jsleaker-env
jsleaker-env\Scripts\activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. (If needed) Install Playwright browsers:

```powershell
playwright install
```

---

## 🛠 Setup Roadmap for Kali Linux (CRITICAL)

Kali often requires a fresh venv installation due to compilation requirements. Follow these steps exactly:

1. Install base dependencies:

```bash
sudo apt update
sudo apt install python3-pip python3-venv build-essential python3-dev -y
```

2. Clone repository:

```bash
git clone https://github.com/jonyhossan110/JS-Leaker.git
cd JS-Leaker
```

3. Create a clean virtual environment:

```bash
python3 -m venv jsleaker-env
source jsleaker-env/bin/activate
```

4. Install core Python libraries manually:

```bash
pip install --upgrade pip
pip install bs4 requests playwright
```

5. Install Playwright browsers (Python target):

```bash
python3 -m playwright install
```

> Do NOT use Node-specific installs like `npm i -D playwright` in this Python workflow. The correct command is `python3 -m playwright install`.

---

## ▶️ Usage

```bash
python3 main.py -u https://example.com
```

Common options:

- `-u`, `--url`: Target URL to scan (required)
- `-t`, `--threads`: Number of worker threads (default from code)
- `-o`, `--output`: Path to output report

Example:

```bash
python3 main.py -u https://example.com -t 8 -o output/scan_report.txt
```

## 📂 Output Structure

The tool generates reports in `output/`:

- `output/scan_report.txt`: Detailed scan results with per-script discoveries, line context, and severity tags.
- `output/report.txt`: High-level summary with total URLs processed, number of secrets found, and severity breakdown.

## ⚠️ Disclaimer

This tool is intended for authorized security testing only. Misuse may be illegal.

- Use only on assets you own or have written permission to test
- Respect responsible disclosure and scope boundaries
- Do not use for unauthorized scanning or intrusion

---

## 🗂 Core Files

- `main.py`: CLI entry point
- `collector.py`: JavaScript URL extraction
- `scanner.py`: Secret detection engine
- `downloader.py`: Parallel file fetching
- `utils.py`: helpers and logging

## 📜 License

Licensed under MIT. See [LICENSE](LICENSE).


