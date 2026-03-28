# Go Binary Integration

This folder contains a starter design for integrating an ultra-fast Go module into CookieInspector.

## How it fits

- Python remains the orchestration layer and report generator.
- Playwright handles JS-driven browser collection.
- Go can provide high-performance subdomain discovery, crawling, or parallel enumeration.
- The Go module can emit JSON or a plain list of URLs that Python consumes.

## Recommended workflow

1. Build the Go binary:
   ```bash
   go build -o bin/fast_crawler.exe fast_crawler.go
   ```

2. Run the binary from Python:
   ```python
   import subprocess
   result = subprocess.run(['bin/fast_crawler.exe', '--url', target_url, '--max-pages', '50', '--output', 'bin/crawl-output.json'], capture_output=True, text=True)
   ```

3. Load the Go output in Python:
   ```python
   import json
   pages = json.loads(Path('bin/crawl-output.json').read_text())
   ```

4. Pass the discovered URLs into `scan_target(...)` as `pages` or `deep_scan` results.

## Integration points

- `scanner.scan_target()` can accept an external crawl list from the Go binary.
- `collector.collect_with_playwright()` will then visit those pages and collect browser cookies.
- `main.py` can be extended to add a `--gorun` or `--go-crawler` flag.

## Why Go?

- Go routines and network I/O make scanning hundreds of subdomains or endpoints much faster than a single-threaded Python crawler.
- A Go binary can export results in JSON and stay isolated from the Python runtime.
- Use Go for `dns`, `http`, and `subdomain bruteforce`; Python continues to handle the browser cookie audit.
