# CookieInspector Pro

HexaCyberLab Hybrid Scanner is a professional cookie and JavaScript security analysis toolkit. CookieInspector Pro combines cookie auditing with the embedded JS-Leaker engine for deep JavaScript discovery, dynamic scanning, and remediation-ready reporting.

CookieInspector Pro scans browser cookie artifacts, scores security risk, generates structured reports, and organizes output in timestamped folders for each scan.

## Key Features

- Multi-target scanning from a `targets.txt` file
- Deep crawl mode for internal page discovery
- Baseline comparison for regression tracking
- Risk and classification scoring for cookies
- Professional remediation recommendations
- Output formats: `json`, `csv`, `table`, `header`, `html`
- Automatically organizes output under `output/<target>_<timestamp>/`

## Installation

### Linux / macOS

```bash
cd CookieInspector
./setup.sh
```

### Windows

```cmd
cd CookieInspector
setup.bat
```

### Manual install

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Usage

### Single target scan

```bash
python main.py --url https://example.com --format json
```

### Multi-target scan

```bash
python main.py --multi --targets targets.txt --format html
```

### Deep scanning

```bash
python main.py --url https://example.com --deep --max-pages 25 --format html
```

### Baseline workflows

```bash
python main.py --url https://example.com --save-baseline baseline.json
python main.py --url https://example.com --baseline baseline.json --format json
```

## Output Organization

CookieInspector Pro creates an organized result folder for each scan. Example:

- `output/example_com_20260415_131500/example_com.json`

If `--output` is provided as a directory, the report will be written into that directory with a generated filename.

## Data & Recommendations

A professional recommendation library is included at `data/recommendations.json`. The report will translate risk findings into concrete remediation guidance.

## Sample Targets

See `targets.txt` for example targets and quick onboarding.

## Notes

- Close the browser before scanning to avoid locked browser cookie DB issues.
- `pdfkit` requires a system `wkhtmltopdf` binary to export PDF files.
- `playwright` is optional but recommended for advanced scanning workflows.

## Project Structure

- `main.py`: CLI orchestration and scan entrypoint
- `scanner.py`: target scanning, deep crawl, baseline compare
- `collector.py`: browser cookie extraction
- `analyzer.py`: cookie enrichment and scoring
- `reporter.py`: report generation and recommendation rendering
- `data/recommendations.json`: remediation guidance library

## License

Provided for professional cookie auditing and security research.

