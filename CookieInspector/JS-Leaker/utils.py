#!/usr/bin/env python3
"""
utils.py - Helper utilities for JS-Leaker

Provides:
- safe, cross-platform logging
- directory helpers
- regex-based secret detection helpers
- report generation helpers

"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import os
import re
import requests
import urllib3
import time
import math
import json
import sqlite3

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

# Disable SSL warnings from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def safe_print(message: str):
    """Print safely for terminals with limited encoding support."""
    if message is None:
        message = ''
    try:
        print(message)
    except UnicodeEncodeError:
        try:
            print(str(message).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
        except Exception:
            print(str(message).encode('ascii', 'ignore').decode('ascii', 'ignore'))
    except Exception:
        pass

# Constants and tuning
TIMEOUT = 15
DEFAULT_REQUEST_TIMEOUT = 10
REQUEST_PAUSE_SECS = 0.5
MAX_RETRIES = 3
MAX_JS_COUNT = 500
MAX_FILE_SIZE_MB = 2  # Skip files >2MB
MAX_CONCURRENT = 8
MAX_SCRIPTS = 1000
MAX_CONTEXT_LINES = 6

# Common libraries to ignore (by filename or content hash)
IGNORED_LIBRARIES = {
    'filenames': {'jquery.min.js', 'jquery.js', 'bootstrap.min.js', 'bootstrap.js', 'swagger-ui-bundle.js', 'swagger-ui-standalone-preset.js'},
    'hashes': set()  # Will populate with known hashes if needed
}


def print_info(message: str):
    """Print info message with [INFO] prefix."""
    safe_print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}" if HAS_COLORAMA else f"[INFO] {message}")


def print_success(message: str):
    """Print success message with [SUCCESS] prefix."""
    safe_print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}" if HAS_COLORAMA else f"[SUCCESS] {message}")


def print_warning(message: str):
    """Print warning message with [WARNING] prefix."""
    safe_print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}" if HAS_COLORAMA else f"[WARNING] {message}")


def print_error(message: str):
    """Print error message with [ERROR] prefix."""
    safe_print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}" if HAS_COLORAMA else f"[ERROR] {message}")


def print_dashboard():
    """Print a professional colorized ASCII art dashboard for JS-Leaker."""
    if HAS_COLORAMA:
        # ASCII art with color codes - Clear JS-LEAKER display
        dashboard = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}                                                                     {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}╔═══════╗{Style.RESET_ALL}{Fore.RED}╔═══════╗{Style.RESET_ALL}                                           {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}║ J S -{Style.RESET_ALL}{Fore.RED}║ LEAKER{Style.RESET_ALL}                                         {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}╚═══════╝{Style.RESET_ALL}{Fore.RED}╚═══════╝{Style.RESET_ALL}                                           {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}                                                                     {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}        {Fore.YELLOW}JavaScript Secret Scanner & Extractor{Style.RESET_ALL}                        {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}║{Style.RESET_ALL}                                                                     {Fore.CYAN}║{Style.RESET_ALL}
{Fore.CYAN}╚═══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}┌─────────────────────────────────────────────────────────────────┐{Style.RESET_ALL}
{Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}Created By:{Style.RESET_ALL} Md. Jony Hassain (HexaCyberLab)                  {Fore.GREEN}│{Style.RESET_ALL}
{Fore.GREEN}│{Style.RESET_ALL}  {Fore.CYAN}LinkedIn:{Style.RESET_ALL}   https://www.linkedin.com/in/md-jony-hassain/    {Fore.GREEN}│{Style.RESET_ALL}
{Fore.GREEN}└─────────────────────────────────────────────────────────────────┘{Style.RESET_ALL}
"""
    else:
        # Fallback plain ASCII art (no colors)
        dashboard = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                     ║
║  ╔═══════╗ ╔═══════╗                                              ║
║  ║ J S - ║ ║ LEAKER║                                              ║
║  ╚═══════╝ ╚═══════╝                                              ║
║                                                                     ║
║        JavaScript Secret Scanner & Extractor                       ║
║                                                                     ║
╚═══════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────┐
│  Created By: Md. Jony Hassain (HexaCyberLab)                    │
│  LinkedIn:   https://www.linkedin.com/in/md-jony-hassain/        │
└─────────────────────────────────────────────────────────────────┘
"""
    safe_print(dashboard)


def log_print(message: str):
    """Print a message safely to console and logging.

    Ensures non-fatal behavior on Windows consoles with limited encodings.
    """
    try:
        if message is None:
            message = ''
        try:
            safe_msg = str(message)
        except Exception:
            safe_msg = repr(message)
        try:
            print(safe_msg)
        except UnicodeEncodeError:
            print(safe_msg.encode('ascii', 'ignore').decode('ascii', 'ignore'))
        try:
            logging.info(safe_msg)
        except Exception:
            pass
    except Exception:
        try:
            print('[LOG ERROR]')
        except Exception:
            pass


def setup_logging(logfile: str = 'js-leaker.log'):
    """Configure logging handlers for file + console.

    Uses UTF-8 file encoding and a console handler. If file handler creation
    fails, we continue with console-only logging.
    """
    handlers = []
    try:
        fh = logging.FileHandler(logfile, encoding='utf-8')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        handlers.append(fh)
    except Exception:
        pass
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    handlers.append(ch)

    logging.basicConfig(level=logging.INFO, handlers=handlers)


def ensure_directories(*dirs: str):
    """Create directories if they don't exist. Ignores empty entries."""
    for directory in dirs:
        if not directory:
            continue
        Path(directory).mkdir(parents=True, exist_ok=True)


def safe_requests_get(url, session=None, timeout=DEFAULT_REQUEST_TIMEOUT, **kwargs):
    """Robust GET with retries, timeout, and rate-limiting."""
    s = session or requests.Session()
    kwargs.setdefault('verify', False)
    kwargs.setdefault('headers', {'User-Agent': 'Mozilla/5.0 (compatible)'});
    last_exception = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = s.get(url, timeout=timeout, **kwargs)
            resp.raise_for_status()
            time.sleep(REQUEST_PAUSE_SECS)
            return resp
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exception = e
            log_print(f"Request failed ({attempt}/{MAX_RETRIES}) for {url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_PAUSE_SECS)
            continue
        except requests.exceptions.HTTPError as e:
            raise
        except requests.exceptions.RequestException as e:
            last_exception = e
            log_print(f"RequestException ({attempt}/{MAX_RETRIES}) for {url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(REQUEST_PAUSE_SECS)
            continue
    if last_exception is not None:
        raise last_exception


def shannon_entropy(value: str) -> float:
    """Calculate Shannon entropy for a string."""
    if not value:
        return 0.0
    freq = {c: value.count(c) / len(value) for c in set(value)}
    return -sum(p * math.log2(p) for p in freq.values())


def is_high_entropy(candidate: str, threshold: float = 4.5) -> bool:
    """Check if string is likely a high-entropy secret."""
    return shannon_entropy(candidate) >= threshold


def maybe_beautify_js(content: str) -> str:
    """Attempt to beautify JS content for better matching."""
    try:
        import jsbeautifier
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        return jsbeautifier.beautify(content, opts)
    except Exception:
        return content


def write_json_report(detailed_results: List[Dict], output_path: str = 'output/scan_report.json') -> None:
    ensure_directories(os.path.dirname(output_path) or '.')
    payload = {
        'generated': datetime.now().isoformat(),
        'files': detailed_results,
    }
    with open(output_path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print_success(f'JSON report saved: {output_path}')


def write_html_report(detailed_results: List[Dict], output_path: str = 'output/scan_report.html') -> None:
    ensure_directories(os.path.dirname(output_path) or '.')
    colors = {
        'CRITICAL': '#ff4d4d',
        'HIGH': '#ff8800',
        'MEDIUM': '#ffdb4d',
        'LOW': '#4dff4d',
    }
    rows = []
    for res in detailed_results:
        for f in res.get('findings', []):
            color = colors.get(f.get('severity', 'LOW').upper(), '#eeeeee')
            rows.append(
                f"<tr style='background:{color};'><td>{res.get('file')}</td><td>{f.get('severity')}</td><td>{f.get('type')}</td><td>{f.get('match')}</td><td>{f.get('line')}</td></tr>"
            )
    html_body = """
<html><head><meta charset='utf-8'><title>JS-Leaker HTML Report</title></head><body>
<h1>JS-Leaker Report</h1>
<table border='1' cellpadding='6' cellspacing='0'>
<tr><th>File</th><th>Severity</th><th>Type</th><th>Match</th><th>Line</th></tr>
""" + '\n'.join(rows) + "</table></body></html>"
    with open(output_path, 'w', encoding='utf-8') as fh:
        fh.write(html_body)
    print_success(f'HTML report saved: {output_path}')


def db_init(path: str = 'js_leaker_state.db') -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans (
                 id INTEGER PRIMARY KEY,
                 url TEXT UNIQUE,
                 status TEXT,
                 last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS findings (
                 id INTEGER PRIMARY KEY,
                 scan_id INTEGER,
                 file TEXT,
                 type TEXT,
                 match TEXT,
                 severity TEXT,
                 line INTEGER,
                 context TEXT,
                 FOREIGN KEY(scan_id) REFERENCES scans(id)
                 )''')
    conn.commit()
    return conn


def mark_scan_state(conn: sqlite3.Connection, url: str, state: str):
    try:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO scans (url, status, last_updated) VALUES (?, ?, CURRENT_TIMESTAMP)", (url, state))
        conn.commit()
    except Exception as e:
        log_print(f"Could not update scan state: {e}")


# SECRET PATTERNS: (name, regex, severity)
# Severity: HIGH, MEDIUM, LOW
SECRET_PATTERNS: List[Tuple[str, re.Pattern, str]] = [
    ('JWT Token', re.compile(r"\beyJ[\w-]+\.[\w-]+\.[\w-]+\b"), 'HIGH'),
    ('AWS Access Key ID', re.compile(r"\bAKIA[0-9A-Z]{16}\b"), 'HIGH'),
    ('AWS Secret Access Key', re.compile(r"\b[0-9a-zA-Z/+]{40}\b"), 'HIGH'),
    ('Firebase URL', re.compile(r"https?://[\w.-]+\.firebaseio\.com"), 'HIGH'),
    ('Google API Key', re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"), 'HIGH'),
    ('Slack Token', re.compile(r"\bxox[baprs]-[0-9A-Za-z-]+\b"), 'HIGH'),
    ('Password in clear', re.compile(r"\bpass(word)?\s*[:=]\s*['\"]?[^\s'\"]{6,60}['\"]?\b", re.I), 'HIGH'),
    ('Private RSA Key', re.compile(r"-----BEGIN (RSA )?PRIVATE KEY-----"), 'HIGH'),
    ('OAuth Bearer', re.compile(r"\bBearer\s+[A-Za-z0-9\-_.]+=*\b"), 'MEDIUM'),
    ('Basic Auth Base64', re.compile(r"\bBasic\s+[A-Za-z0-9+/=]{20,}\b"), 'MEDIUM'),
    ('Generic API Key', re.compile(r"\bapi[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9-_]{16,64}['\"]?\b", re.I), 'MEDIUM'),
    ('OAuth Token', re.compile(r"\boauth_token\s*[:=]\s*['\"]?[A-Za-z0-9\-_.]{8,}['\"]?\b", re.I), 'MEDIUM'),
    ('Slack Webhook URL', re.compile(r"https?://hooks\.slack\.com/services/[A-Z0-9]{9,}/[A-Z0-9]{9,}/[a-zA-Z0-9]{24,}"), 'HIGH'),
    ('Twilio Auth Token', re.compile(r"\bSK[0-9a-fA-F]{32}\b"), 'HIGH'),
    ('SendGrid API Key', re.compile(r"\bSG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}\b"), 'HIGH'),
    ('OpenAI API Key', re.compile(r"\bsk-[A-Za-z0-9]{48,56}\b"), 'HIGH'),
]


def detect_secrets_in_text(text: str) -> List[Dict]:
    """Scan given text for known secret patterns.

    Returns list of findings with keys: type, match, severity, context, line
    """
    findings = []
    if not text:
        return findings

    lines = text.splitlines()

    for name, pattern, severity in SECRET_PATTERNS:
        try:
            for m in pattern.finditer(text):
                match_text = m.group(0)
                if len(match_text) >= 20 and not is_high_entropy(match_text):
                    continue
                # approximate line number
                start_pos = m.start()
                line_no = text.count('\n', 0, start_pos) + 1
                # context: few lines around the hit
                start_line = max(0, line_no - 1 - (MAX_CONTEXT_LINES // 2))
                end_line = min(len(lines), start_line + MAX_CONTEXT_LINES)
                context = '\n'.join(lines[start_line:end_line])
                findings.append({
                    'type': name,
                    'match': match_text,
                    'severity': severity,
                    'line': line_no,
                    'context': context
                })
        except re.error:
            continue

    # Deduplicate by match content
    seen = set()
    dedup = []
    for f in findings:
        key = (f['type'], f['match'])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(f)

    return dedup


def should_skip_file(filepath: str) -> bool:
    """Check if file should be skipped: size >2MB, empty, or ignored library."""
    try:
        if not os.path.exists(filepath):
            return True
        size = os.path.getsize(filepath)
        if size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return True
        if size == 0:
            return True
        filename = os.path.basename(filepath).lower()
        if filename in IGNORED_LIBRARIES['filenames']:
            return True
        # Could add hash check here if needed
        return False
    except Exception:
        return True


def save_text_file(path: str, content: str, max_bytes: int = 5 * 1024 * 1024):
    """Write content safely to path with UTF-8 encoding and size cap."""
    try:
        ensure_directories(Path(path).parent.as_posix())
        with open(path, 'w', encoding='utf-8', errors='replace') as fh:
            fh.write(content[:max_bytes])
        return True
    except Exception as e:
        print_error(f"Could not save file {path}: {e}")
        return False


def write_scan_report(detailed_results: List[Dict], output_path: str = 'output/scan_report.txt') -> None:
    """Write a readable scan report enumerating files and findings."""
    ensure_directories(os.path.dirname(output_path) or '.')
    lines = []
    lines.append('JS-Leaker Scan Report')
    lines.append('=' * 60)
    lines.append(f'Generated: {datetime.now().isoformat()}')
    lines.append('')

    total = 0
    for res in detailed_results:
        file = res.get('file')
        findings = res.get('findings', [])
        lines.append(f'FILE: {file} ({len(findings)} findings)')
        lines.append('-' * 60)
        for f in findings:
            total += 1
            lines.append(f"[{f.get('severity')}] {f.get('type')} - Line {f.get('line')}")
            lines.append(f"Match: {f.get('match')}")
            ctx = f.get('context', '')
            if ctx:
                lines.append('Context:')
                lines.extend(['  ' + ln for ln in ctx.splitlines()])
            lines.append('')
        lines.append('')

    lines.insert(3, f'Total Findings: {total}')

    try:
        Path(output_path).write_text('\n'.join(lines), encoding='utf-8')
        print_success(f'Report saved: {output_path}')
    except Exception as e:
        print_error(f'Could not write scan report: {e}')
