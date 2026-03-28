from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from urllib.parse import urlparse

from collector import get_cookies
from analyzer import filter_cookies, run_js_leaker, scan_javascript_files, scan_local_js_files
from crawler import deep_scan, get_base_domain, normalize_url
from scorer import enrich_cookie, detect_duplicates, normalize_origin
from baseline import load_baseline, save_baseline, compare_cookies
from utils.logging import get_logger
from utils.progress import print_stage

logger = get_logger(__name__)


def normalize_target_url(target: str) -> str:
    if not target.startswith(('http://', 'https://')):
        return 'https://' + target.lstrip('/')
    return target


def load_targets_file(path: Optional[str]) -> List[str]:
    if not path:
        return []
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f'Targets file not found: {path}')
    targets: List[str] = []
    for line in file_path.read_text(encoding='utf-8').splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith('#'):
            targets.append(cleaned)
    return targets


def build_origins(urls: Iterable[str], include_subdomains: bool = False) -> List[str]:
    origins = set()
    for raw in urls:
        normalized = normalize_target_url(raw)
        parsed = urlparse(normalized)
        host = parsed.netloc.lower()
        if not host:
            continue
        origins.add(host)
        origins.add('.' + host)
        if include_subdomains:
            root = get_base_domain(host)
            origins.add(root)
            origins.add('.' + root)
    return sorted(origins)


def get_target_domains(target_urls: Iterable[str]) -> List[str]:
    domains = set()
    for raw in target_urls:
        parsed = urlparse(normalize_target_url(raw))
        if parsed.netloc:
            domains.add(parsed.netloc.lower())
            domains.add(get_base_domain(parsed.netloc))
    return sorted(domains)


def scan_target(target: str,
                profile: Optional[str] = None,
                names: Optional[List[str]] = None,
                include_expired: bool = False,
                include_subdomains: bool = False,
                deep: bool = False,
                js_deep: bool = False,
                max_pages: int = 12) -> Dict:
    target_url = normalize_target_url(target)
    target_domains = get_target_domains([target_url])
    print_stage(f'Start scan for {target_url}')

    pages = []
    if deep:
        print_stage('Deep mode enabled: crawling internal pages')
        pages = deep_scan(target_url, max_pages=max_pages)
        print_stage(f'Found {len(pages)} internal pages in deep scan')

    origins = build_origins([target_url] + pages, include_subdomains=include_subdomains)
    if not origins:
        origins = build_origins([target_url], include_subdomains=include_subdomains)

    scan_pages = [target_url]
    for page_url in pages:
        normalized = normalize_target_url(page_url)
        if normalized not in scan_pages:
            scan_pages.append(normalized)

    try:
        raw = get_cookies(
            target_url,
            browsers=['chrome'],
            profile=profile,
            origins=origins,
            pages=scan_pages,
            names=names,
        )
    except Exception as exc:
        logger.warning(f'Collection failed for {target_url}: {exc}')
        raw = {'cookies': [], 'warnings': [str(exc)]}

    cookies = filter_cookies(raw['cookies'], names=names, include_expired=include_expired)
    enriched = [enrich_cookie(cookie, target_domains=target_domains) for cookie in cookies]
    duplicate_items = detect_duplicates(enriched)
    js_analysis = scan_javascript_files(scan_pages or [target_url])
    js_leaker_result = None
    if js_deep:
        js_leaker_result = run_js_leaker(target_url)
        if js_leaker_result.get('downloaded_files'):
            js_analysis.extend(scan_local_js_files(js_leaker_result['downloaded_files']))
        if js_leaker_result.get('error'):
            raw.setdefault('warnings', []).append(js_leaker_result['error'])

    summary = {
        'target': target_url,
        'pages': len(pages),
        'origins': origins,
        'found_cookies': len(cookies),
        'duplicates': duplicate_items,
        'risk_counts': {
            'Critical': sum(1 for cookie in enriched if cookie.get('risk') == 'Critical'),
            'High': sum(1 for cookie in enriched if cookie.get('risk') == 'High'),
            'Medium': sum(1 for cookie in enriched if cookie.get('risk') == 'Medium'),
            'Low': sum(1 for cookie in enriched if cookie.get('risk') == 'Low'),
        },
    }

    return {
        'target': target_url,
        'cookies': enriched,
        'warnings': raw.get('warnings', []),
        'summary': summary,
        'js_analysis': js_analysis,
        'js_leaker': js_leaker_result,
        'baseline_diff': None,
    }


def scan_targets(url: Optional[str] = None,
                 targets_file: Optional[str] = None,
                 multi: bool = False,
                 profile: Optional[str] = None,
                 names: Optional[List[str]] = None,
                 include_expired: bool = False,
                 include_subdomains: bool = False,
                 deep: bool = False,
                 js_deep: bool = False,
                 max_pages: int = 12,
                 baseline_path: Optional[str] = None,
                 save_baseline_path: Optional[str] = None) -> Dict:
    targets: List[str] = []
    if targets_file:
        targets.extend(load_targets_file(targets_file))
    if multi and not targets_file:
        targets.extend(load_targets_file('targets.txt'))
    if url:
        targets.append(url)

    if not targets:
        raise ValueError('No scan target provided. Use --url or --targets.')

    results = []
    for index, target in enumerate(targets, start=1):
        print_stage(f'Queueing target {index}/{len(targets)}: {target}')
        result = scan_target(target,
                             profile=profile,
                             names=names,
                             include_expired=include_expired,
                             include_subdomains=include_subdomains,
                             deep=deep,
                             js_deep=js_deep,
                             max_pages=max_pages)
        if baseline_path:
            baseline_file = Path(baseline_path)
            if baseline_file.exists():
                baseline = load_baseline(baseline_file).get('cookies', [])
                result['baseline_diff'] = compare_cookies(baseline, result['cookies'])
                print_stage(f'Baseline comparison completed for {target}')
            else:
                result['warnings'].append(f'Baseline file not found: {baseline_path}')
        if save_baseline_path:
            save_baseline(result['cookies'], Path(save_baseline_path))
            print_stage(f'Saved baseline to {save_baseline_path}')
        results.append(result)

    total_warnings = [warning for result in results for warning in result['warnings']]
    return {
        'targets': results,
        'total_targets': len(results),
        'total_cookies': sum(len(result['cookies']) for result in results),
        'warnings': total_warnings,
    }
