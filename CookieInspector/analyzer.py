"""Cookie analyzer: filter, enrich.

Pattern from Sweet-cookie normalize/filter logic.

Source:
- Tool: Sweet-cookie
- File: public.ts normalizeNames/origins, util/expire.ts implied
- Purpose: Post-collection process (expired filter, name filter).

Why: Clean data for report.

Mod Tips:
- Add risk score (sensitive names).
- Domain validation.

"""

import json
import os
import subprocess
import sys
from pathlib import Path
import re
from typing import List, Dict, Optional, Sequence, Set
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests

from scorer import enrich_cookie


def chrome_now() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1_000_000) + 11644473600000000


def filter_cookies(cookies: List[Dict],
                   names: Optional[List[str]] = None,
                   include_expired: bool = False,
                   target_domains: Optional[Sequence[str]] = None) -> List[Dict]:
    """Filter by names, expire."""
    filtered: List[Dict] = []
    name_set = set(names or [])
    now_unix = chrome_now()

    for cookie in cookies:
        if name_set and cookie.get('name') not in name_set:
            continue
        expires_utc = cookie.get('expires_utc')
        if expires_utc and not include_expired and expires_utc < now_unix:
            continue
        filtered.append(cookie)

    return filtered

def analyze_cookies(cookies: List[Dict], target_domains: Optional[Sequence[str]] = None) -> List[Dict]:
    return [enrich_cookie(cookie, target_domains=target_domains) for cookie in cookies]

COOKIE_ASSIGNMENT_RE = re.compile(r'document\.cookie\s*[:+]?=')
SENSITIVE_JS_TOKEN_RE = re.compile(r'\b(password|secret|token|apikey|api_key|access_token|auth|session|cookie)\b', re.I)
SCRIPT_SRC_RE = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']', re.I)
JS_ENDPOINT_RE = re.compile(r'["\']((?:https?:)?//[^"\']+|(?:/|\.{1,2}/)[^"\']+\.(?:js|json|php|asp|aspx|xml|cgi|ajax|api)[^"\']*)["\']', re.I)
FETCH_ENDPOINT_RE = re.compile(r'fetch\(\s*["\']([^"\']+)["\']', re.I)
XHR_OPEN_RE = re.compile(r'\.open\(\s*["\'](?:GET|POST|PUT|DELETE|PATCH)["\']\s*,\s*["\']([^"\']+)["\']', re.I)
DEFAULT_JS_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/126.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'application/javascript, text/javascript, */*; q=0.01',
}

# Use a path relative to the repository root so JS-Leaker can be invoked on any machine.
ROOT_DIR = Path(__file__).resolve().parents[1]
JS_LEAKER_DIR = ROOT_DIR / 'JS-Leaker'
JS_LEAKER_MAIN = JS_LEAKER_DIR / 'main.py'


def _normalize_js_url(src: str, base_url: str) -> str:
    if src.startswith('//'):
        parsed = urlparse(base_url)
        return f'{parsed.scheme}:{src}'
    return urljoin(base_url, src)


def _extract_js_urls(html: str, base_url: str) -> Set[str]:
    urls: Set[str] = set()
    for match in SCRIPT_SRC_RE.finditer(html):
        src = match.group(1).strip()
        if not src:
            continue
        urls.add(_normalize_js_url(src, base_url))
    return urls


def _extract_js_endpoints(js_url: str, content: str) -> Set[str]:
    endpoints: Set[str] = set()
    for regex in (JS_ENDPOINT_RE, FETCH_ENDPOINT_RE, XHR_OPEN_RE):
        for match in regex.finditer(content):
            endpoint = match.group(1).strip()
            if not endpoint:
                continue
            endpoints.add(_normalize_js_url(endpoint, js_url))
    return endpoints


def _scan_js_content(js_url: str, content: str) -> Optional[Dict[str, object]]:
    matches = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        if COOKIE_ASSIGNMENT_RE.search(line) or SENSITIVE_JS_TOKEN_RE.search(line):
            snippet = line.strip()[:200]
            if COOKIE_ASSIGNMENT_RE.search(line):
                match_type = 'document.cookie assignment'
            else:
                match_type = 'sensitive string'
            keywords = SENSITIVE_JS_TOKEN_RE.findall(line)
            matches.append({
                'line': line_number,
                'type': match_type,
                'snippet': snippet,
                'keywords': [k for k in keywords] if keywords else [],
            })

    endpoints = sorted(_extract_js_endpoints(js_url, content))
    if not matches and not endpoints:
        return None

    result: Dict[str, object] = {
        'script_url': js_url,
        'matches': matches,
    }
    if endpoints:
        result['endpoints'] = endpoints
    return result

# Use a path relative to the repository root so JS-Leaker can be invoked on any machine.
ROOT_DIR = Path(__file__).resolve().parents[1]
JS_LEAKER_DIR = ROOT_DIR / 'JS-Leaker'
JS_LEAKER_MAIN = JS_LEAKER_DIR / 'main.py'


def _extract_domain_from_url(url: str) -> str:
    parsed = urlparse(url if '://' in url else f'//{url}', scheme='https')
    host = parsed.netloc.lower()
    if host.startswith('www.'):
        host = host[4:]
    return host


def run_js_leaker(url: str,
                  output_dir: Optional[str] = None,
                  dynamic: bool = True) -> Dict[str, object]:
    if not JS_LEAKER_MAIN.exists():
        return {
            'error': 'JS-Leaker entrypoint not found',
            'downloaded_files': [],
            'findings': [],
            'summary': {},
        }

    output_root = Path(output_dir) if output_dir else Path(__file__).resolve().parents[0] / 'data' / 'js_leaker'
    output_root.mkdir(parents=True, exist_ok=True)
    report_file = output_root / 'scan_report.json'

    cmd = [sys.executable, str(JS_LEAKER_MAIN), '-u', url, '-o', str(report_file), '--format', 'json']
    if dynamic:
        cmd.append('--dynamic')
    cmd.append('--silent-dashboard')

    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        completed = subprocess.run(
            cmd,
            cwd=str(JS_LEAKER_DIR),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            check=False,
        )
    except Exception as exc:
        return {
            'error': f'JS-Leaker execution failed: {exc}',
            'downloaded_files': [],
            'findings': [],
            'summary': {},
        }

    if completed.returncode != 0:
        return {
            'error': f'JS-Leaker failed: {completed.stderr.strip() or completed.stdout.strip()}',
            'downloaded_files': [],
            'findings': [],
            'summary': {},
        }

    parsed_report: Dict[str, object] = {}
    if report_file.exists():
        try:
            parsed_report = json.loads(report_file.read_text(encoding='utf-8'))
        except Exception:
            parsed_report = {}

    download_root = output_root / _extract_domain_from_url(url)
    js_files: List[str] = []
    if download_root.exists():
        js_files.extend(str(p) for p in sorted(download_root.rglob('*.js')))

    inline_root = JS_LEAKER_DIR / 'data' / 'inline'
    if inline_root.exists():
        js_files.extend(str(p) for p in sorted(inline_root.rglob('*.js')))

    if not js_files:
        js_files.extend(str(p) for p in sorted(output_root.rglob('*.js')))

    files_payload = parsed_report.get('files', []) if isinstance(parsed_report.get('files', []), list) else []
    summary = {
        'report_path': str(report_file),
        'downloaded_files': len(js_files),
        'findings': sum(len(item.get('findings', [])) for item in files_payload),
    }

    return {
        'report': parsed_report,
        'downloaded_files': js_files,
        'findings': files_payload,
        'summary': summary,
    }


def scan_local_js_files(file_paths: Sequence[str], max_files: int = 200) -> List[Dict[str, object]]:
    scans: List[Dict[str, object]] = []
    visited: Set[str] = set()
    for file_path in file_paths:
        if len(scans) >= max_files:
            break
        if file_path in visited:
            continue
        visited.add(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as fh:
                body = fh.read()
            result = _scan_js_content(file_path, body)
            if result:
                scans.append(result)
        except Exception:
            continue
    return scans


def scan_javascript_files(pages: Sequence[str], max_files: int = 50, timeout: int = 10) -> List[Dict[str, object]]:
    """Scan JS files linked from the target pages for document.cookie and hardcoded sensitive values."""
    scans: List[Dict[str, object]] = []
    session = requests.Session()
    session.headers.update(DEFAULT_JS_HEADERS)
    session.verify = False

    visited_scripts: Set[str] = set()

    for page_url in pages:
        if len(visited_scripts) >= max_files:
            break
        try:
            response = session.get(page_url, timeout=timeout)
            if response.status_code != 200 or 'html' not in response.headers.get('Content-Type', '').lower():
                continue
            html = response.text
        except Exception:
            continue

        script_urls = _extract_js_urls(html, page_url)
        for js_url in sorted(script_urls):
            if len(visited_scripts) >= max_files:
                break
            if js_url in visited_scripts:
                continue
            visited_scripts.add(js_url)
            try:
                js_response = session.get(js_url, timeout=timeout)
                if js_response.status_code != 200:
                    continue
                body = js_response.text
            except Exception:
                continue
            result = _scan_js_content(js_url, body)
            if result:
                scans.append(result)

    return scans


def to_cookie_header(cookies: List[Dict], sort: str = 'name') -> str:
    """HTTP Cookie header, dedupe name.
    
    Like Sweet-cookie toCookieHeader.
    """
    seen = {}
    items = []
    for c in sorted(cookies, key=lambda x: x['name'] if sort == 'name' else 0):
        name = c['name']
        if name not in seen:
            seen[name] = c['value']
            items.append(f'{name}={c["value"]}')
    
    return '; '.join(items)

if __name__ == '__main__':
    # Test data
    test_cookies = [{'name': 'session', 'value': 'abc', 'domain': '.example.com', 'path': '/', 'secure': True, 'httponly': True}]
    print(to_cookie_header(test_cookies))

