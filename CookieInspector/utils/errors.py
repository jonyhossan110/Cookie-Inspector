from pathlib import Path
"""Custom exceptions.

From SweetCookieKit BrowserCookieError mapping (notFound, accessDenied, loadFailed).

Source:
- Tool: SweetCookieKit
- File: BrowserCookieImporter.swift ~lines 150-250 (mapSafariError etc.)
- Purpose: Granular errors for forensics.

Improved: Hierarchy, str repr with context.

Modification Tips:
- Subclass for specific DB errors.
- Example: raise ProfileNotFound(profile=path)

"""

class CookieInspectorError(Exception):
    """Base error."""
    pass

class ProfileNotFound(CookieInspectorError):
    def __init__(self, browser: str, profile: Path):
        self.browser = browser
        self.profile = profile
        super().__init__(f"No {browser} profile/DB found at {profile}")

class AccessDenied(CookieInspectorError):
    def __init__(self, path: Path):
        self.path = path
        super().__init__(f"Access denied to cookie DB: {path}")

class LoadFailed(CookieInspectorError):
    def __init__(self, browser: str, error: str):
        self.browser = browser
        super().__init__(f"Failed to load {browser} cookies: {error}")

class NoCookiesFound(CookieInspectorError):
    """No matching cookies (not error)."""
    pass

