#!/usr/bin/env python3
"""
main.py - Orchestrates JS-Leaker

Steps performed:
- Parse CLI
- Collect static + dynamic JS via `collector.py`
- Download external JS in parallel to domain-specific folders
- Scan all saved JS for secrets with patterns in `utils.py`
- Produce `output/scan_report.txt` (detailed) and `output/report.txt` (severity summary)

Usage examples:
  python main.py -u https://example.com -t 6 -o output/scan_report.txt

"""

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import hashlib
import requests

from utils import (
    setup_logging,
    log_print,
    print_info,
    print_success,
    print_warning,
    print_error,
    ensure_directories,
    detect_secrets_in_text,
    write_scan_report,
    should_skip_file,
    print_dashboard,
)
from collector import JSCollector


def _safe_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = parsed.path.split('/')[-1] or 'script.js'
    # include host hash for uniqueness
    h = hashlib.sha1(url.encode('utf-8')).hexdigest()[:8]
    fname = f"{parsed.netloc.replace('.', '_')}__{h}__{name}".replace('/', '_')
    return fname


def extract_domain_from_url(url: str) -> str:
    """Extract domain name from URL for folder creation.
    
    Examples:
    - https://example.com -> example.com
    - https://subdomain.example.com -> example.com
    - https://example.co.uk -> example.co.uk
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    # Remove www. prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def download_and_save(url: str, target_dir: str, domain: str, seen_hashes: set, timeout: int = 15) -> str:
    """Download a JS URL and save to domain-specific folder within target_dir.
    
    Structure: target_dir/[domain]/[original_filename].js
    Returns local path or ''.
    """
    try:
        resp = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (compatible)'
        })
        resp.raise_for_status()
        content = resp.text
        h = hashlib.sha1(content.encode('utf-8', errors='replace')).hexdigest()
        if h in seen_hashes:
            return ''  # Duplicate
        seen_hashes.add(h)
        
        # Create domain-specific folder
        domain_folder = os.path.join(target_dir, domain)
        ensure_directories(domain_folder)
        
        fname = _safe_filename_from_url(url)
        path = os.path.join(domain_folder, fname)
        with open(path, 'w', encoding='utf-8', errors='replace') as fh:
            fh.write(content)
        return path
    except Exception as e:
        log_print(f'Warning: could not download {url}: {e}')
        return ''


def scan_files(file_paths: list) -> list:
    """Scan a list of file paths for secrets using utils.detect_secrets_in_text.

    Returns list of dicts: {'file': path, 'findings': [...]}
    """
    results = []
    for fp in file_paths:
        if should_skip_file(fp):
            continue
        try:
            with open(fp, 'r', encoding='utf-8', errors='replace') as fh:
                text = fh.read()
            findings = detect_secrets_in_text(text)
            if findings:
                results.append({'file': fp, 'findings': findings})
        except Exception as e:
            log_print(f'Error scanning {fp}: {e}')
    return results


def merge_deduplicate_findings(all_results: list) -> list:
    """Merge findings and remove duplicates across files (same match + type).

    Keeps the first occurrence's file and line.
    """
    seen = set()
    merged = []
    for r in all_results:
        file = r.get('file')
        for f in r.get('findings', []):
            key = (f.get('type'), f.get('match'))
            if key in seen:
                continue
            seen.add(key)
            merged.append({'file': file, **f})
    return merged


def write_severity_summary(merged_findings: list, outpath: str = 'output/report.txt'):
    lines = []
    counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    for f in merged_findings:
        sev = f.get('severity', 'LOW')
        counts[sev] = counts.get(sev, 0) + 1

    lines.append('JS-Leaker Severity Summary')
    lines.append('=' * 40)
    lines.append(f"HIGH: {counts['HIGH']}")
    lines.append(f"MEDIUM: {counts['MEDIUM']}")
    lines.append(f"LOW: {counts['LOW']}")
    lines.append(f"Total Unique Findings: {len(merged_findings)}")
    lines.append('')
    lines.append('Detailed entries:')
    for f in merged_findings:
        file_name = f.get('file') or 'unknown'
        lines.append(f"[{f.get('severity')}] {f.get('type')} in {os.path.basename(file_name) if file_name != 'unknown' else 'unknown'} (line {f.get('line')})")

    try:
        ensure_directories(os.path.dirname(outpath) or '.')
        with open(outpath, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines))
        log_print(f'Severity summary saved: {outpath}')
    except Exception as e:
        log_print(f'ERROR: Could not save severity summary: {e}')


def main():
    print_dashboard()
    setup_logging()

    parser = argparse.ArgumentParser(description='JS-Leaker - JavaScript Secret Scanner')
    parser.add_argument('-u', '--url', required=True, help='Target URL (e.g., https://example.com)')
    parser.add_argument('-t', '--threads', type=int, default=4, help='Number of worker threads for download/scan')
    parser.add_argument('-o', '--output-file', default='output/scan_report.txt', help='Output file for detailed report')
    args = parser.parse_args()

    target = args.url
    if not target.endswith('/'):
        target += '/'
    workers = max(1, min(args.threads, 32))
    out_file = args.output_file
    out_dir = os.path.dirname(out_file) or 'output'

    # Extract domain for folder structure
    domain = extract_domain_from_url(target)

    ensure_directories('data/external', 'data/inline', out_dir, os.path.join(out_dir, domain))

    print_info(f"Target: {target}")
    print_info(f"Domain: {domain}")
    print_info(f"Workers: {workers}")
    print_info(f"Output folder: {os.path.join(out_dir, domain)}")

    # Quick check if target is reachable
    try:
        resp = requests.head(target, timeout=10)
        if resp.status_code >= 400:
            print_warning(f"Target returned status {resp.status_code}")
    except Exception as e:
        print_warning(f"Could not reach target: {e}")

    collector = JSCollector()
    print_info("Collecting JavaScript files...")
    collect_res = collector.collect(target)
    external_urls = collect_res.get('external_js', [])
    inline_paths = collect_res.get('inline_js', [])

    print_success(f"Found {len(external_urls)} external JS, {len(inline_paths)} inline JS")

    # Download external JS in parallel to domain-specific folder
    downloaded = []
    seen_hashes = set()
    if external_urls:
        print_info("Downloading external JavaScript files...")
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(download_and_save, url, out_dir, domain, seen_hashes): url for url in external_urls}
            for fut in as_completed(futures):
                path = fut.result()
                if path:
                    downloaded.append(path)
        print_success(f"Downloaded {len(downloaded)} external JS files to {os.path.join(out_dir, domain)}/")

    all_js_files = list(set(inline_paths + downloaded))

    if not all_js_files:
        print_error("No JavaScript files found to scan.")
        return

    print_info(f"Scanning {len(all_js_files)} files for secrets...")
    # Use ThreadPoolExecutor for scanning IO-bound file reads
    scan_results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(scan_files, [fp]): fp for fp in all_js_files}
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                scan_results.extend(res)

    # Merge and dedupe findings
    merged = merge_deduplicate_findings(scan_results)

    # Write detailed report and severity summary
    detailed_results = []
    # Convert merged back into grouped by file for write_scan_report
    files_map = {}
    for m in merged:
        fpath = m.pop('file')
        files_map.setdefault(fpath, []).append(m)
    for fpath, items in files_map.items():
        detailed_results.append({'file': fpath, 'findings': items})

    write_scan_report(detailed_results, output_path=out_file)
    write_severity_summary(merged, outpath=os.path.join(out_dir, 'report.txt'))

    print_success("Scan complete. Reports saved to output directory.")
    print_success(f"JavaScript files saved to: {os.path.join(out_dir, domain)}/")


if __name__ == '__main__':
    main()
