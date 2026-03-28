"""Path utilities for browser profile discovery.

Extracted pattern from Sweet-cookie chromium paths detection.
Improved: pathlib, cross-platform, env overrides.

Source:
- Tool: Sweet-cookie
- Files: providers/chromium/paths.ts, util/fs.ts (inferred patterns)
- Purpose: Locate Cookies DB (e.g., Chrome 'User Data/Default/Cookies')

Modification Tips:
- Add custom browser paths via BROWSER_PATHS env JSON.
- Extend find_profiles() for custom logic.
Example: paths.find_chrome_profiles(profile='Profile 1')

"""

import json
import os
import platform
from pathlib import Path
from typing import Iterator, List, Optional

_system = platform.system().lower()

BROWSER_PATHS = {
    'chrome': {
        'darwin': [
            Path('~') / 'Library' / 'Application Support' / 'Google' / 'Chrome' / 'Default',
            Path('~') / 'Library' / 'Application Support' / 'Google' / 'Chrome' / 'Profile 1',
            Path('~') / 'Library' / 'Application Support' / 'BraveSoftware' / 'Brave-Browser' / 'Default',
        ],
        'linux': [
            Path('~') / '.config' / 'google-chrome' / 'Default',
            Path('~') / '.config' / 'google-chrome-beta' / 'Default',
            Path('~') / '.config' / 'BraveSoftware' / 'Brave-Browser' / 'Default',
        ],
        'win32': [
            Path(os.environ.get('LOCALAPPDATA', '')) / 'Google' / 'Chrome' / 'User Data' / 'Default',
            Path(os.environ.get('LOCALAPPDATA', '')) / 'Google' / 'Chrome' / 'User Data' / 'Profile 1',
        ]
    },
    'firefox': {
        'darwin': [Path('~') / 'Library' / 'Application Support' / 'Firefox' / 'Profiles'],
        'linux': [Path('~') / '.mozilla' / 'firefox'],
        'win32': [Path(os.environ.get('APPDATA', '')) / 'Mozilla' / 'Firefox' / 'Profiles'],
    }
}

def expand_path(path_str: str) -> Path:
    """Expand ~ and env vars in path."""
    return Path(os.path.expandvars(os.path.expanduser(path_str)))

def find_profiles(browser: str, profile: Optional[str] = None) -> Iterator[Path]:
    """Yield cookie DB paths for browser/profile.
    
    Args:
        browser: 'chrome' or 'firefox'
        profile: Specific profile name/path (override).
    """
    if profile:
        yield expand_path(profile) / 'Cookies'
        return
    
    paths = BROWSER_PATHS.get(browser, {}).get(_system, [])
    for base in paths:
        p = expand_path(str(base))
        if p.exists():
            cookie_db = p / 'Cookies'
            if cookie_db.exists():
                yield cookie_db

def get_default_profiles(browser: str) -> List[Path]:
    """Get all available profiles/DBs."""
    return list(find_profiles(browser))

if __name__ == '__main__':
    import sys
    browser = sys.argv[1] if len(sys.argv) > 1 else 'chrome'
    print(list(get_default_profiles(browser)))

