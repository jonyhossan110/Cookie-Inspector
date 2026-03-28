#!/usr/bin/env python3
"""
scanner.py - Production-ready JS secret scanner.
"""

import os
import re
from typing import List, Dict
from pathlib import Path
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import log_print, print_info, print_error, print_warning, MAX_FILE_SIZE_MB, MAX_BASE64_CANDIDATES, MAX_CONTEXT_LINES, MAX_CONCURRENT

class JSScanner:
    """
    Production JS secret scanner with threading, expanded patterns.
    """
    
    MAX_CONTENT_SIZE = int(MAX_FILE_SIZE_MB * 1024 * 1024)
    
    SECRET_PATTERNS = {
        'API Keys': re.compile(r'api[_-]?key["\']?\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})', re.I),
        'AWS Keys': re.compile(r'(AKIA[0-9A-Z]{16})'),
        'GCP Keys': re.compile(r'AIza[0-9A-Za-z_-]{35}'),
        'Stripe Keys': re.compile(r'sk_live_[0-9a-zA-Z]{24,}'),
        'GitHub Tokens': re.compile(r'ghp_[0-9A-Za-z]{36}'),
        'Passwords': re.compile(r'(?i)password["\']?\s*[=:]\s*["\']?([^"\']{4,})'),
        'Private Keys': re.compile(r'-----BEGIN [A-Z ]+ PRIVATE KEY-----'),
        'Tokens': re.compile(r'(?i)(token|secret)["\']?\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})'),
        'JWT Tokens': re.compile(r'eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+'),
        'API Endpoints': re.compile(r'(?:https?://[^ \s]+/api/|["\']/api/)[^ \s"\']{5,}'),
    }
    
    BASE64_PATTERN = re.compile(r'[A-Za-z0-9+/]{20,}={0,2}')
    
    def __init__(self):
        self.context_lines = MAX_CONTEXT_LINES
    
    def scan(self, data_dir: str, output_dir: str, output_file: str = None, max_workers: int = None):
        """
        Threaded scan of JS files.

        :param data_dir: directory containing JS files (will be searched recursively)
        :param output_dir: directory where reports are written
        :param output_file: explicit path for the severity-summary output
        :param max_workers: maximum thread workers (capped by MAX_CONCURRENT)
        """
        # allow caller to influence worker count
        if max_workers is not None:
            try:
                self.max_workers = int(max_workers)
            except Exception:
                self.max_workers = None
        os.makedirs(output_dir, exist_ok=True)

        # Recursively find all JS files (external + inline saved in subdirs)
        js_files = list(Path(data_dir).rglob('*.js'))
        print_info(f'Scanning {len(js_files)} JS files...')

        results = []
        # max_workers may be provided via caller; fall back to MAX_CONCURRENT
        workers = MAX_CONCURRENT
        try:
            # callers may set self.max_workers attribute
            if hasattr(self, 'max_workers') and isinstance(self.max_workers, int):
                workers = max(1, min(self.max_workers, MAX_CONCURRENT))
        except Exception:
            workers = MAX_CONCURRENT

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_file = {executor.submit(self._scan_file, str(js_file)): js_file for js_file in js_files}
            for future in as_completed(future_to_file):
                js_file = future_to_file[future]
                try:
                    findings = future.result()
                    if findings:
                        results.append({
                            'file': js_file.name,
                            'findings': findings
                        })
                except Exception as e:
                    print_error(f'Scan error {js_file.name}: {str(e)}')
        
        self._save_report(results, output_dir, output_file)
        print_success(f'Found secrets in {len(results)} files')
    
    def _scan_file(self, filepath: str) -> List[Dict]:
        """
        Scan single file with proper line numbering.
        """
        stat = os.stat(filepath)
        if stat.st_size > self.MAX_CONTENT_SIZE:
            print_warning(f'Skipped large: {os.path.basename(filepath)}')
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            print_error(f'Read error {os.path.basename(filepath)}: {str(e)}')
            return []
        
        lines = content.splitlines()
        
        # Raw scan
        raw_findings = []
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                finding = {
                    'type': secret_type,
                    'match': match.group(1) or match.group(),
                    'line': line_num,
                    'context': self._get_context(lines, line_num)
                }
                raw_findings.append(finding)
        
        # Base64 + rescan
        decoded_findings = []
        for b64_match in list(self.BASE64_PATTERN.finditer(content))[:MAX_BASE64_CANDIDATES]:
            try:
                decoded_text = base64.b64decode(b64_match.group()).decode('utf-8', errors='ignore')
                if len(decoded_text) > 10 and decoded_text.isprintable():
                    decoded_secrets = self._scan_decoded(decoded_text)
                    line_num = content[:b64_match.start()].count('\n') + 1
                    for ds in decoded_secrets:
                        finding = {
                            'type': f'[Base64] {ds["type"]}',
                            'match': ds["match"],
                            'line': line_num,
                            'context': self._get_context(lines, line_num) + '\n  [Base64]'
                        }
                        decoded_findings.append(finding)
            except:
                pass
        
        all_findings = raw_findings + decoded_findings
        
        # Dedup and sort
        seen = set()
        unique = []
        for f in sorted(all_findings, key=lambda x: (x['line'], x['type'])):
            key = (f['type'], f['match'][:64])
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique
    
    def _scan_decoded(self, text: str) -> List[Dict]:
        """Scan decoded Base64 text."""
        findings = []
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            for match in pattern.finditer(text):
                findings.append({
                    'type': secret_type,
                    'match': match.group(1) or match.group()
                })
        return findings
    
    def _get_context(self, lines: List[str], line_num: int) -> str:
        """Get context lines around match."""
        start = max(0, line_num - self.context_lines - 1)
        end = min(len(lines), line_num + self.context_lines)
        context_lines = []
        for i in range(start, end):
            marker = ' *** MATCH ***' if i + 1 == line_num else ''
            context_lines.append(f'{i+1:3d}|{lines[i][:120]}{marker}')
        return '\n'.join(context_lines)
    
    def _save_report(self, results: List[Dict], output_dir: str, output_file: str = None):
        """
        Save detailed reports.
        """
        report_path = os.path.join(output_dir, 'scan_report.txt')
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('JS-LEAKER SCAN REPORT\n')
                f.write('=' * 60 + '\n\n')
                total_findings = 0
                for result in sorted(results, key=lambda x: len(x['findings']), reverse=True):
                    f.write(f'FILE: {result["file"]} ({len(result["findings"])} findings)\n')
                    f.write('-' * 60 + '\n')
                    for finding in sorted(result['findings'], key=lambda x: x['line']):
                        f.write(f'{finding["type"]}: {finding["match"][:80]}{ "..." if len(finding["match"]) > 80 else "" }\n')
                        f.write(f'  Line {finding["line"]}\n')
                        f.write(f'  Context:\n{finding["context"]}\n')
                        f.write('\n')
                    total_findings += len(result['findings'])
                f.write(f'TOTAL FINDINGS: {total_findings}\n')
                f.write('End of report.\n')
            print_success(f'Report saved: {report_path}')
        except Exception as e:
            print_error(f'Report error: {e}')
        
        from utils import generate_severity_report
        # If an explicit output_file was provided, use it; otherwise place in output_dir/output.txt
        out_path = output_file if output_file else os.path.join(output_dir, 'output.txt')
        try:
            generate_severity_report(results, out_path)
        except Exception as e:
            print_error(f'Error generating severity report: {e}')
