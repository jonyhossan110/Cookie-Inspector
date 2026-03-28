#!/usr/bin/env python3
"""
collector.py - Collect static and dynamic JavaScript from target website.

Features:
- Static collection: parse HTML with BeautifulSoup to find external and inline scripts
- Dynamic collection: render SPA pages with Playwright (headless) to capture
  dynamically injected scripts and inline code
- Save collected JS to `data/external` and `data/inline`
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import hashlib
import os
from pathlib import Path
from typing import List, Dict
import urllib3
from utils import log_print, print_warning, print_error, TIMEOUT, ensure_directories, save_text_file, safe_requests_get, DEFAULT_REQUEST_TIMEOUT

# Disable SSL warnings from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JSCollector:
    """Collect external and inline JS (static + dynamic).

    Methods:
    - collect(url): returns {'external_js': [urls], 'inline_js': [paths_saved]}
    """

    def __init__(self, session: requests.Session = None):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        ensure_directories('data/external', 'data/inline')

    def collect(self, target_url: str, dynamic: bool = False) -> Dict[str, List[str]]:
        """Collect both static and dynamic JS, saving to disk.

        Returns dict with lists: external_js (urls) and inline_js (local file paths)
        """
        external = set()
        inline_paths = []
        inline_hashes = set()  # For deduplication

        # Static collection first
        try:
            resp = safe_requests_get(target_url, session=self.session, timeout=DEFAULT_REQUEST_TIMEOUT)
            html = resp.text
            soup = BeautifulSoup(html, 'html.parser')

            # External script tags
            for s in soup.find_all('script', src=True):
                js_url = urljoin(target_url, s['src'])
                external.add(js_url)

            # Inline script tags
            for s in soup.find_all('script', src=False):
                content = s.string if s.string is not None else s.get_text()
                if content and content.strip():
                    h = hashlib.sha1(content.encode('utf-8', errors='replace')).hexdigest()
                    if h not in inline_hashes:
                        inline_hashes.add(h)
                        p = self._save_inline(content, target_url)
                        if p:
                            inline_paths.append(p)

            # Also pick JS referenced in attributes/hardcoded urls
            for m in re.finditer(r'https?://[^"\'>\s]+\.js(?:\?[^"\'>\s]*)?', html, re.I):
                external.add(m.group(0))

            # Webpack chunk patterns (vendor.js, chunk.js, runtime.js, app.*.js)
            for m in re.finditer(r"(?:(?:https?://|/)[^\s\"'<>]*?(?:chunk|vendor|runtime|app)[^\s\"'<>]*\.js)", html, re.I):
                maybe_url = m.group(0)
                if maybe_url.startswith('http'):
                    external.add(maybe_url)
                else:
                    external.add(urljoin(target_url, maybe_url))

        except Exception as e:
            print_error(f'Static collection failed for {target_url}: {e}')

        # Dynamic collection via Playwright (preferred). Fallback if not available.
        if dynamic:
            try:
                dynamic_ext, dynamic_inline = self._collect_dynamic_playwright(target_url)
                for u in dynamic_ext:
                    external.add(u)
                for content in dynamic_inline:
                    h = hashlib.sha1(content.encode('utf-8', errors='replace')).hexdigest()
                    if h not in inline_hashes:
                        inline_hashes.add(h)
                        p = self._save_inline(content, target_url)
                        if p:
                            inline_paths.append(p)
            except Exception as e:
                print_warning(f'Playwright dynamic collection failed: {e}')

        return {
            'external_js': sorted(list(external)),
            'inline_js': sorted(inline_paths)
        }

    def _save_inline(self, content: str, source_url: str) -> str:
        """Save inline JS content to data/inline with a deterministic filename."""
        try:
            h = hashlib.sha1(content.encode('utf-8', errors='replace')).hexdigest()[:12]
            parsed = urlparse(source_url)
            name = f"{parsed.netloc.replace('.', '_')}_{h}.js"
            path = os.path.join('data', 'inline', name)
            if save_text_file(path, content):
                return path
        except Exception as e:
            print_error(f'Inline save error: {e}')
        return ''

    def _collect_dynamic_playwright(self, url: str):
        """Use Playwright to render the page and extract JS (external + inline).

        Returns (external_urls, inline_contents)
        """
        try:
            # Import locally to allow module absence handling
            from playwright.sync_api import sync_playwright

            external = set()
            inline = []

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=30000)

                # Execute a small script to enumerate scripts
                scripts = page.evaluate('''() => {
                    const out = [];
                    for (const s of document.scripts){
                        out.push({src: s.src || null, text: s.src ? null : s.innerText});
                    }
                    return out;
                }''')

                for s in scripts:
                    src = s.get('src')
                    text = s.get('text')
                    if src:
                        external.add(src)
                    elif text and text.strip():
                        inline.append(text)

                # Also grab the rendered HTML and search for .js references not caught above
                rendered = page.content()
                for m in re.finditer(r'https?://[^"\'>\s]+\.js(?:\?[^"\'>\s]*)?', rendered, re.I):
                    external.add(m.group(0))
                for m in re.finditer(r"(?:(?:https?://|/)[^\s\"'<>]*?(?:chunk|vendor|runtime|app)[^\s\"'<>]*\.js)", rendered, re.I):
                    maybe_url = m.group(0)
                    if maybe_url.startswith('http'):
                        external.add(maybe_url)
                    else:
                        external.add(urljoin(url, maybe_url))

                try:
                    browser.close()
                except Exception:
                    pass

            return sorted(external), inline
        except Exception as e:
            # Surface errors upwards; caller will log and continue
            raise

