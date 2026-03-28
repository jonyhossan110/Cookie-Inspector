from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence
from urllib.parse import urlparse
import re

CHROME_EPOCH_OFFSET = 11644473600000000


def chrome_timestamp_to_unix(expires_utc: Optional[int]) -> Optional[int]:
    if expires_utc is None or expires_utc == 0:
        return None
    return int((expires_utc - CHROME_EPOCH_OFFSET) / 1_000_000)


def get_now_unix() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def get_base_domain(host: str) -> str:
    parts = [p for p in host.lower().split('.') if p]
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return host.lower()


def normalize_origin(value: str) -> str:
    if '://' in value:
        parsed = urlparse(value)
        return parsed.netloc.lower()
    return value.lower().strip()


def classify_cookie_name(name: str) -> str:
    name = name.lower()
    if name.startswith(('sess', 'session', 'sid', 'auth', 'jwt')) or 'token' in name:
        return 'session'
    if any(key in name for key in ('_ga', '_gid', '_gat', 'utm', 'analytics', 'fbp', 'gclid', 'advert', 'track', 'trk', 'pixel')):
        return 'analytics'
    if any(key in name for key in ('ads', 'ad', 'tracking', 'trk', 'pixel', 'collect', 'cookieconsent')):
        return 'tracking'
    return 'other'


def compute_risk(cookie: Dict, target_domains: Optional[Sequence[str]] = None) -> Dict:
    score = 0
    reasons: List[str] = []
    classification = classify_cookie_name(cookie.get('name', ''))
    secure = bool(cookie.get('secure'))
    httponly = bool(cookie.get('httponly'))
    expires_utc = cookie.get('expires_utc')
    expiration = chrome_timestamp_to_unix(expires_utc)
    now = get_now_unix()
    expired = expiration is not None and expiration < now

    if classification == 'session':
        score += 2
        reasons.append('Session-specific cookie name')
    if not secure:
        score += 1
        reasons.append('Not Secure')
    if not httponly:
        score += 1
        reasons.append('Missing HttpOnly')
    if classification == 'tracking':
        score += 2
        reasons.append('Tracking-related cookie name')
    elif classification == 'analytics':
        score += 1
        reasons.append('Analytics/measurement cookie name')
    same_site = str(cookie.get('samesite', '')).strip().lower()
    if same_site == 'none' and not secure:
        score += 2
        reasons.append('SameSite=None without Secure')
    if expires_utc is None or expires_utc == 0:
        reasons.append('Session cookie')
    if expired:
        score += 1
        reasons.append('Expired cookie')
    if target_domains:
        domain = cookie.get('domain', '').lstrip('.')
        if domain and all(not domain.endswith(normalize_origin(td)) for td in target_domains):
            score += 1
            reasons.append('Third-party or unrelated domain')
    value = cookie.get('value', '')
    if value and len(value) > 1024:
        score += 1
        reasons.append('Very large cookie value')

    if score >= 5:
        label = 'Critical'
    elif score >= 4:
        label = 'High'
    elif score >= 2:
        label = 'Medium'
    else:
        label = 'Low'

    return {
        'classification': classification,
        'risk_score': score,
        'risk': label,
        'risk_reasons': reasons,
        'expired': expired,
        'expires_at': expiration,
    }


def enrich_cookie(cookie: Dict, target_domains: Optional[Sequence[str]] = None) -> Dict:
    enriched = dict(cookie)
    if 'expires_utc' in enriched and enriched['expires_utc']:
        enriched['expires_timestamp'] = chrome_timestamp_to_unix(enriched['expires_utc'])
    else:
        enriched['expires_timestamp'] = None
    enriched.update(compute_risk(enriched, target_domains=target_domains))
    return enriched


def detect_duplicates(cookies: List[Dict]) -> List[Dict]:
    seen = {}
    duplicates = []
    for cookie in cookies:
        key = (cookie.get('name'), cookie.get('domain'), cookie.get('path'))
        if key in seen:
            if seen[key] == 1:
                duplicates.append({'name': key[0], 'domain': key[1], 'path': key[2], 'count': 2})
            else:
                for entry in duplicates:
                    if entry['name'] == key[0] and entry['domain'] == key[1] and entry['path'] == key[2]:
                        entry['count'] += 1
                        break
            seen[key] += 1
        else:
            seen[key] = 1
    for cookie in cookies:
        key = (cookie.get('name'), cookie.get('domain'), cookie.get('path'))
        cookie['duplicate'] = seen.get(key, 0) > 1
    return duplicates
