import sys
import time


def print_stage(message: str) -> None:
    """Emit a stage log for CLI progress."""
    timestamp = time.strftime('%H:%M:%S')
    sys.stdout.write(f'[{timestamp}] {message}\n')
    sys.stdout.flush()


def progress_bar(current: int, total: int, width: int = 36) -> None:
    """Render a simple CLI progress bar."""
    if total <= 0:
        return
    ratio = min(max(current / total, 0.0), 1.0)
    filled = int(ratio * width)
    bar = '[' + '=' * filled + '>' + ' ' * max(width - filled - 1, 0) + ']'
    sys.stdout.write(f'\r{bar} {current}/{total}')
    if current >= total:
        sys.stdout.write('\n')
    sys.stdout.flush()
