from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from typing import List, Set, Optional
import ssl
import socket
import logging
import asyncio

try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None

logger = logging.getLogger(__name__)


class LinkExtractor(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.links: Set[str] = set()

    def handle_starttag(self, tag, attrs):
        if tag.lower() not in {'a', 'link', 'area', 'form', 'iframe'}:
            return
        for name, value in attrs:
            if name.lower() in {'href', 'src', 'action'} and value:
                self.links.add(value)


def normalize_url(target: str) -> str:
    parsed = urlparse(target)
    if not parsed.scheme:
        target = 'https://' + target.lstrip('/')
    return target


def get_base_domain(host: str) -> str:
    parts = [p for p in host.lower().split('.') if p]
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return host

REAL_BROWSER_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/126.0.0.0 Safari/537.36'
)


def extract_links(html: str, base_url: str) -> Set[str]:
    parser = LinkExtractor(base_url)
    try:
        parser.feed(html)
    except Exception:
        return set()
    links: Set[str] = set()
    for link in parser.links:
        absolute = urljoin(base_url, link)
        parsed = urlparse(absolute)
        if parsed.scheme in {'http', 'https'}:
            normalized = parsed.geturl().split('#')[0]
            links.add(normalized)
    return links


def deep_scan(start_url: str, max_pages: int = 15, timeout: int = 6) -> List[str]:
    """Crawl same-root pages and return visited URLs."""
    start_url = normalize_url(start_url)
    parsed = urlparse(start_url)
    base_root = get_base_domain(parsed.netloc)
    visited: List[str] = []
    queue: List[str] = [start_url]
    ssl_context = ssl.create_default_context()

    if aiohttp is None:
        while queue and len(visited) < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            try:
                request = Request(url, headers={'User-Agent': REAL_BROWSER_USER_AGENT})
                with urlopen(request, timeout=timeout, context=ssl_context) as response:
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' not in content_type.lower():
                        visited.append(url)
                        continue
                    body = response.read().decode('utf-8', errors='ignore')
            except (HTTPError, URLError, socket.timeout, ssl.SSLError, ConnectionResetError, OSError, ValueError) as exc:
                logger.warning(f'Crawler skipped {url}: {exc}')
                visited.append(url)
                continue
            visited.append(url)
            links = extract_links(body, url)
            for link in sorted(links):
                parsed_link = urlparse(link)
                if parsed_link.netloc and get_base_domain(parsed_link.netloc) == base_root and link not in visited and link not in queue:
                    queue.append(link)
        return visited

    async def _fetch_page(session: aiohttp.ClientSession, url: str) -> Optional[str]:
        try:
            async with session.get(url, timeout=timeout) as response:
                if response.status != 200:
                    logger.warning(f'Crawler skipped {url}: HTTP {response.status}')
                    return None
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type.lower():
                    return None
                return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError, UnicodeDecodeError, ValueError) as exc:
            logger.warning(f'Crawler skipped {url}: {exc}')
            return None

    async def _async_scan() -> List[str]:
        visited_set = set()
        queue_items = [start_url]
        results: List[str] = []
        connector = aiohttp.TCPConnector(ssl=False)
        headers = {'User-Agent': REAL_BROWSER_USER_AGENT, 'Accept-Language': 'en-US,en;q=0.9'}
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(connector=connector, headers=headers, timeout=timeout_obj) as session:
            while queue_items and len(results) < max_pages:
                batch = []
                while queue_items and len(batch) < 8 and len(results) + len(batch) < max_pages:
                    url = queue_items.pop(0)
                    if url in visited_set:
                        continue
                    visited_set.add(url)
                    batch.append(url)
                if not batch:
                    break
                tasks = [asyncio.create_task(_fetch_page(session, url)) for url in batch]
                pages = await asyncio.gather(*tasks)
                for url, body in zip(batch, pages):
                    results.append(url)
                    if not body:
                        continue
                    links = extract_links(body, url)
                    for link in sorted(links):
                        parsed_link = urlparse(link)
                        if parsed_link.netloc and get_base_domain(parsed_link.netloc) == base_root and link not in visited_set and link not in queue_items:
                            queue_items.append(link)
        return results

    return asyncio.run(_async_scan())
