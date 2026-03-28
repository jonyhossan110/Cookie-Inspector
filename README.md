# HexaCyberLab Cookie Inspector Pro

**Md. Jony Hassain**  
LinkedIn: https://www.linkedin.com/in/md-jony-hassain/

Cookie Inspector Pro is a hybrid security scanner for cookie auditing and JavaScript analysis. It combines the CookieInspector engine with the integrated JS-Leaker engine to identify cookie risk, discover internal pages, and scan JavaScript assets for cookie-setting behavior and hardcoded secrets.

## Project Structure

- `CookieInspector/` - core cookie auditing engine, reporting, CLI, and scan orchestration
- `JS-Leaker/` - JavaScript analysis engine used by Cookie Inspector Pro for deep JS collection and secret scanning
- `.git/` - repository metadata

## What it does

- Collects browser cookies and evaluates security risk
- Supports single-target and multi-target scanning
- Performs deep crawl mode to discover internal application pages
- Filters cookies by name, expiration, and subdomain matching
- Integrates JS-Leaker for deep JavaScript asset collection and secret detection
- Generates structured output in JSON, CSV, table, header, or HTML formats

## JS-Leaker Integration

When `--js-deep` is enabled, Cookie Inspector Pro invokes the JS-Leaker engine from the repository root using a relative path to `JS-Leaker/main.py`.

The integration flow is:

1. `CookieInspector` performs cookie collection and initial JS analysis.
2. `--js-deep` triggers `run_js_leaker()` in `CookieInspector/analyzer.py`.
3. JS-Leaker downloads external and inline JavaScript assets for the target URL.
4. Downloaded JS files are rescanned locally to detect cookie assignments, sensitive tokens, and suspicious JavaScript endpoints.
5. Results are merged into the final report and any JS-Leaker errors are surfaced as warnings.

## Installation

### Recommended

```bash
cd CookieInspector
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### Windows

```cmd
cd CookieInspector
setup.bat
```

### Linux / macOS

```bash
cd CookieInspector
./setup.sh
```

## Available CLI Options

`main.py` exposes the following command-line options:

- `--url`, `-u` : target URL or origin for cookie matching
- `--targets`, `-t` : path to a targets file with one URL/domain per line
- `--multi` : use multi-target mode with `targets.txt`
- `--browser`, `-b` : browser backend (chrome only)
- `--profile`, `-p` : custom browser profile path
- `--names`, `-n` : filter cookie names (space-separated)
- `--include-expired` : include expired cookies in results
- `--include-subdomains` : match cookies for subdomains of the target
- `--deep` : enable deep scan mode across internal pages
- `--js-deep` : run JS-Leaker for deep JavaScript collection and merge results
- `--max-pages` : maximum pages to crawl in deep scan (default: 12)
- `--baseline` : load a baseline JSON file for comparison
- `--save-baseline` : save current scan results to a baseline JSON file
- `--format`, `-f` : output format: `json`, `csv`, `table`, `header`, `html`
- `--output`, `-o` : output file or directory (`-` generates an organized output folder)

## Usage Examples

### Single target scan

```bash
cd CookieInspector
python main.py --url https://example.com --format html --output output
```

### Deep scan with JS-Leaker integration

```bash
cd CookieInspector
python main.py --url https://example.com --deep --js-deep --format json
```

### Multi-target scan from a file

```bash
cd CookieInspector
python main.py --targets targets.txt --multi --format table
```

## Output

The scanner creates organized output folders under `CookieInspector/output/` and exports a raw cookie JSON file alongside the selected report format. HTML output includes the branded `HexaCyberLab Cookie Inspector Pro` report header.

## Notes

- Make sure `playwright` is installed and Chromium is available.
- Use `requirements.txt` inside `CookieInspector/` for the full dependency set.
- If `--js-deep` is enabled, the tool runs the integrated JS-Leaker engine and includes JS findings in the final report.

## License

Use this repository for security research and professional cookie analysis.
