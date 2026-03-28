#!/usr/bin/env python3
"""Cookie Inspector Pro CLI.

Professional browser cookie auditing engine with multi-target scanning,
deep crawling, risk scoring, and baseline comparison.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from scanner import scan_targets
from reporter import Reporter
from utils.logging import get_logger

logger = get_logger(__name__)

BANNER = r'''
 ____                _        ___                     _             
/ ___|___   ___ | | _(_) ___|_ _|_ __  ___ _ __   ___  ___| |_ ___  _ __ 
| |   / _ \ / _ \| |/ / |/ _ \ | || '_ \/ __| '_ \ / _ \/ __| __/ _ \| '__|
| |__| (_) | (_) |   <| |  __/ | || | | \__ \ |_) |  __/ (__| || (_) | |   
 \____\___/ \___/|_|\_\_|\___|___|_| |_|___/ .__/ \___|\___|\__\___/|_|   
                                            |_|                            

┌─────────────────────────────────────────────────────────────────┐
│  Created By: Md. Jony Hassain (HexaCyberLab)                    │
│  LinkedIn:   https://www.linkedin.com/in/md-jony-hassain/       │
└─────────────────────────────────────────────────────────────────┘

      HexaCyberLab Cookie Inspector Pro - Professional Cookie Audit
'''


def print_banner() -> None:
    try:
        from rich.console import Console

        console = Console()
        console.print(BANNER, style='bold cyan')
    except Exception:
        print(BANNER)


def slugify_target(value: str) -> str:
    cleaned = re.sub(r'[^A-Za-z0-9]+', '_', value.lower()).strip('_')
    return cleaned or 'scan'


def build_output_path(user_output: str, target_key: str, fmt: str) -> Path:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_target = slugify_target(target_key)

    if user_output in ('-', 'stdout'):
        output_dir = Path('output') / f'{safe_target}_{timestamp}'
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / f'{safe_target}.{fmt}'

    output_path = Path(user_output)
    if output_path.exists() and output_path.is_dir():
        output_path = output_path / f'{safe_target}.{fmt}'
    elif output_path.suffix == '':
        output_path.mkdir(parents=True, exist_ok=True)
        output_path = output_path / f'{safe_target}.{fmt}'
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Cookie Inspector Pro: professional cookie scanning and audit tool.'
    )
    parser.add_argument('--url', '-u', help='Target URL/origin for cookie match')
    parser.add_argument('--targets', '-t', help='Path to targets file with one URL/domain per line')
    parser.add_argument('--multi', action='store_true', help='Enable multi-target mode using targets list')
    parser.add_argument('--browser', '-b', default='chrome', choices=['chrome'], help='Browser backend (chrome only)')
    parser.add_argument('--profile', '-p', help='Custom profile path')
    parser.add_argument('--names', '-n', nargs='+', help='Filter cookie names (space separated)')
    parser.add_argument('--include-expired', action='store_true', help='Include expired cookies')
    parser.add_argument('--include-subdomains', action='store_true', help='Match cookies for subdomains of the target')
    parser.add_argument('--deep', action='store_true', help='Enable deep scan mode across internal pages')
    parser.add_argument('--js-deep', action='store_true', help='Run JS-Leaker deep JS collection and merge results')
    parser.add_argument('--max-pages', type=int, default=12, help='Maximum pages to crawl in deep scan')
    parser.add_argument('--baseline', help='Load a baseline JSON file to compare current results against')
    parser.add_argument('--save-baseline', help='Save current scan results to a baseline JSON file')
    parser.add_argument('--format', '-f', default='json', choices=['json', 'csv', 'table', 'header', 'html'], help='Output format')
    parser.add_argument('--output', '-o', default='-', help='Output file or directory (- creates organized output folder)')

    args = parser.parse_args()

    if not args.url and not args.targets and not args.multi:
        parser.error('Provide --url, --targets, or --multi to start scanning.')

    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONUTF8', '1')

    print_banner()

    target_key = args.url or args.targets or 'multi'
    output_path = build_output_path(args.output, target_key, args.format)

    try:
        data = scan_targets(
            url=args.url,
            targets_file=args.targets,
            multi=args.multi,
            profile=args.profile,
            names=args.names,
            include_expired=args.include_expired,
            include_subdomains=args.include_subdomains,
            deep=args.deep,
            js_deep=args.js_deep,
            max_pages=args.max_pages,
            baseline_path=args.baseline,
            save_baseline_path=args.save_baseline,
        )
        Reporter(args.format, output_path).generate(data)
        raw_output = output_path.parent / 'cookies.json'
        raw_output.write_text(json.dumps(data, indent=2), encoding='utf-8')
        print(f'Output written to: {output_path}')
        print(f'Raw cookie JSON exported to: {raw_output}')
    except Exception as exc:
        logger.error(f'Error: {exc}')
        sys.exit(1)


if __name__ == '__main__':
    main()

