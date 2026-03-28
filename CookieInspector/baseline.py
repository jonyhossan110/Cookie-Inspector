import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

CookieKey = Tuple[str, str, str]


def cookie_key(cookie: Dict) -> CookieKey:
    return (cookie.get('name', ''), cookie.get('domain', ''), cookie.get('path', ''))


def load_baseline(path: Path) -> Dict[str, List[Dict]]:
    text = path.read_text(encoding='utf-8')
    return json.loads(text)


def save_baseline(cookies: Iterable[Dict], path: Path) -> None:
    payload = {'cookies': list(cookies)}
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def compare_cookies(old: Iterable[Dict], new: Iterable[Dict]) -> Dict[str, List[Dict]]:
    old_map = {cookie_key(cookie): cookie for cookie in old}
    new_map = {cookie_key(cookie): cookie for cookie in new}

    added = []
    removed = []
    changed = []

    for key, current in new_map.items():
        if key not in old_map:
            added.append(current)
        else:
            previous = old_map[key]
            if any(previous.get(field) != current.get(field) for field in ['value', 'secure', 'httponly', 'expires_utc']):
                changed.append({'before': previous, 'after': current})
    for key, previous in old_map.items():
        if key not in new_map:
            removed.append(previous)

    return {'added': added, 'removed': removed, 'changed': changed}
