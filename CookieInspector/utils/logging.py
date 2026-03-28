"""Structured logging and warnings.

Pattern from Sweet-cookie {cookies, warnings: string[]}, oracle logging.

Source:
- Tool: Sweet-cookie
- File: packages/core/src/public.ts lines ~10-50 (warnings.push)
- Purpose: Non-fatal diagnostics separate from cookies.

Why needed: Cybersecurity tool - audit extraction issues (locked DB, no cookies).

Modification Tips:
- Add JSON formatter for reports.
- Levels: DEBUG profile search, INFO cookies found, WARN access denied.

"""
import logging
from typing import List
from pathlib import Path

class WarningsLogger:
    def __init__(self):
        self._warnings: List[str] = []
        self.logger = logging.getLogger('CookieInspector')
        self.logger.setLevel(logging.INFO)
    
    def warn(self, msg: str, *args, **kwargs):
        """Add warning (non-fatal)."""
        full_msg = msg.format(*args, **kwargs) if args or kwargs else msg
        self._warnings.append(full_msg)
        self.logger.warning(full_msg)
    
    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg.format(*args, **kwargs) if args or kwargs else msg)
    
    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg.format(*args, **kwargs) if args or kwargs else msg)
    
    @property
    def warnings(self) -> List[str]:
        return self._warnings.copy()
    
    def clear_warnings(self):
        self._warnings.clear()

# Global handler (thread-safe)
warnings_logger = WarningsLogger()

def get_logger(name: str = 'CookieInspector') -> logging.Logger:
    return logging.getLogger(name)

