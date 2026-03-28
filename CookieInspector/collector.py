"""Cookie collection via Playwright Chromium.

Updated to run a headless browser and extract cookies directly from browser
context after page load. This bypasses local browser profile DB access and
works on machines without an installed Chrome profile.

Source:
- Playwright browser automation
- Target URL + crawled internal pages
- page.goto(..., wait_until='networkidle')

"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast
from urllib.parse import urlparse

import urllib3

from utils.logging import warnings_logger

DEFAULT_CHROME_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/126.0.0.0 Safari/537.36'
)

DEFAULT_HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError, sync_playwright
except ImportError:
    sync_playwright = None
    PlaywrightError = Exception
    PlaywrightTimeoutError = Exception


@dataclass
class Cookie:
    name: str
    value: str
    domain: str
    path: str
    secure: bool
    httponly: bool
    expires_utc: Optional[int] = None  # Chrome microsec since 1601
    samesite: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Tuple) -> 'Cookie':
        name, value, domain, path, secure, httponly, expires_utc = row
        return cls(name, value, domain, path, bool(secure), bool(httponly), expires_utc, None)

    @classmethod
    def from_playwright(cls, cookie: Dict[str, Any]) -> 'Cookie':
        return cls(
            name=cookie.get('name', ''),
            value=cookie.get('value', ''),
            domain=cookie.get('domain', ''),
            path=cookie.get('path', '/'),
            secure=bool(cookie.get('secure')),
            httponly=bool(cookie.get('httpOnly')),
            expires_utc=_normalize_playwright_expires(cookie.get('expires')),
            samesite=cookie.get('sameSite') or None,
        )


def normalize_origin_string(origin: str) -> List[str]:
    parsed = urlparse(origin if '://' in origin else f'//{origin}', scheme='https')
    host = parsed.netloc or parsed.path
    if not host:
        return []
    host = host.lower()
    results = [host]
    if not host.startswith('.'):
        results.append(f'.{host}')
    return results


def normalize_origins(url_or_origins: Union[str, List[str]]) -> List[str]:
    """Origins from URL or list, lower-case host variants."""
    origins: List[str] = []
    if isinstance(url_or_origins, str):
        origins = normalize_origin_string(url_or_origins)
    else:
        for origin in url_or_origins:
            origins += normalize_origin_string(origin)
    seen = set()
    deduped: List[str] = []
    for origin in origins:
        if origin and origin not in seen:
            seen.add(origin)
            deduped.append(origin)
    return deduped


def normalize_names(names: Optional[List[str]]) -> Optional[Set[str]]:
    """Allowlist cookie names, trimmed and lowercased."""
    if not names:
        return None
    cleaned = [name.strip() for name in names if name and name.strip()]
    if not cleaned:
        return None
    return set(cleaned)


def cookie_key(cookie: Any) -> str:
    return f"{cookie.get('name','')}|{cookie.get('domain','')}|{cookie.get('path','/')}"


def cookie_matches_filters(cookie: Any, origins: Optional[List[str]], names: Optional[Set[str]]) -> bool:
    if names is not None and cookie.get('name') not in names:
        return False
    if origins:
        domain = cookie.get('domain', '')
        if not host_matches(domain, origins):
            return False
    return True


def host_matches(host: str, origins: List[str]) -> bool:
    """host_key ends with origin or .origin."""
    host_lower = host.lower()
    return any(host_lower.endswith(o) for o in origins)


def _normalize_playwright_expires(expires: Optional[Union[int, float]]) -> Optional[int]:
    if expires is None or expires == 0:
        return None
    return int((float(expires) + 11644473600) * 1_000_000)


def normalize_page_url(value: str) -> str:
    if not value.startswith(('http://', 'https://')):
        return 'https://' + value.lstrip('/')
    return value


def collect_with_playwright(url: str,
                            pages: Optional[List[str]] = None,
                            origins: Optional[List[str]] = None,
                            names: Optional[List[str]] = None) -> Tuple[List[Cookie], List[str]]:
    if sync_playwright is None:
        raise RuntimeError('Playwright is required for browser-based cookie collection. Install playwright and run `playwright install chromium`.')

    urls: List[str] = [normalize_page_url(url)]
    if pages:
        for page in pages:
            normalized = normalize_page_url(page)
            if normalized not in urls:
                urls.append(normalized)

    cookies_map: Dict[str, Cookie] = {}
    warnings: List[str] = []
    normalized_names = normalize_names(names)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
            )
            context = browser.new_context(
                ignore_https_errors=True,
                user_agent=DEFAULT_CHROME_USER_AGENT,
                locale='en-US',
                viewport={'width': 1920, 'height': 1080},
                java_script_enabled=True,
                extra_http_headers=DEFAULT_HEADERS,
            )
            context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
            context.add_init_script("window.navigator.chrome = { runtime: {} };")
            context.add_init_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});")
            context.add_init_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});")
            page = context.new_page()

            for target_url in urls:
                try:
                    page.goto(target_url, wait_until='networkidle', timeout=30000)
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(4000)
                except (PlaywrightTimeoutError, PlaywrightError, Exception) as exc:
                    msg = f'Playwright navigation failed for {target_url}: {exc}'
                    warnings_logger.warn(msg)
                    warnings.append(msg)
                    continue

                for raw_cookie in context.cookies():
                    browser_cookie = cast(Dict[str, Any], raw_cookie)
                    if not cookie_matches_filters(browser_cookie, origins, normalized_names):
                        continue
                    key = cookie_key(browser_cookie)
                    if key not in cookies_map:
                        cookies_map[key] = Cookie.from_playwright(browser_cookie)

            context.close()
            browser.close()
    except Exception as exc:
        msg = f'Playwright browser launch failed: {exc}'
        warnings_logger.warn(msg)
        warnings.append(msg)

    cookies = list(cookies_map.values())
    return cookies, warnings


def get_cookies(url: str,
                browsers: List[str] = ['chrome'],
                profile: Optional[str] = None,
                origins: Optional[List[str]] = None,
                pages: Optional[List[str]] = None,
                names: Optional[List[str]] = None) -> Dict:
    """Main API via Playwright headless Chromium.
    Returns {'cookies': [Cookie], 'warnings': [str]}
    """
    origins = normalize_origins(origins or url)
    warnings_logger.clear_warnings()

    cookies, warnings = collect_with_playwright(url, pages=pages, origins=origins, names=names)

    warnings_logger.info(f'Found {len(cookies)} cookies for {origins}')
    return {'cookies': [c.to_dict() for c in cookies], 'warnings': warnings}


if __name__ == '__main__':
    import sys
    from pprint import pprint

    result = get_cookies(sys.argv[1] if len(sys.argv) > 1 else 'https://google.com')
    pprint(result)
