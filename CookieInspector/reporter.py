"""Report generation.

Patterns from Sweet-cookie toCookieHeader, warnings dump.

Source:
- Tool: Sweet-cookie
- File: public.ts ~140-170 toCookieHeader(dedupe name)
- Purpose: Output formats (JSON/CSV/header/table).

Why: User-friendly cybersecurity reports.

Mod Tips:
- Add HTML report.
- Export to file.

"""

import csv
import json
import html
from typing import Dict, List, Union
from pathlib import Path

from analyzer import to_cookie_header

DATA_DIR = Path(__file__).resolve().parent / 'data'
RECOMMENDATIONS_FILE = DATA_DIR / 'recommendations.json'
try:
    with RECOMMENDATIONS_FILE.open(encoding='utf-8') as pointer:
        RECOMMENDATIONS = json.load(pointer)
except Exception:
    RECOMMENDATIONS = {}

class Reporter:
    def __init__(self, format: str = 'json', output: Union[str, Path] = '-'):
        self.format = format.lower()
        self.output = output if isinstance(output, Path) else Path(output)
    
    def generate(self, data: Dict) -> None:
        """Generate report from {'cookies': [...], 'warnings': [...]}."""
        warnings = data.get('warnings', [])
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  - {w}')
        
        if self.format == 'json':
            content = json.dumps(self._json_payload(data), indent=2)
        elif self.format == 'csv':
            cookies = self._flatten_cookies(data)
            content = self._to_csv(cookies)
        elif self.format == 'header':
            cookies = self._flatten_cookies(data)
            content = to_cookie_header(cookies)
        elif self.format == 'table':
            cookies = self._flatten_cookies(data)
            content = self._to_table(cookies)
        elif self.format == 'html':
            content = self._to_html(data)
        else:
            raise ValueError(f'Unknown format: {self.format}')

        if str(self.output) == '-' or self.output == Path('-'):
            summary = self._render_cli_summary(data)
            if summary:
                print(summary)

        if isinstance(self.output, Path) and self.output.suffix.lower() == '.pdf':
            self._write_pdf(content, self.output)
        elif str(self.output) == '-' or self.output == Path('-'):
            print(content)
        else:
            self.output.write_text(content, encoding='utf-8')
    
    def _to_csv(self, cookies: List[Dict]) -> str:
        import io
        fp = io.StringIO()
        writer = csv.DictWriter(fp, fieldnames=['name', 'value', 'domain', 'path', 'secure', 'httponly', 'expires_utc'])
        writer.writeheader()
        writer.writerows(cookies)
        return fp.getvalue()

    def _to_table(self, cookies: List[Dict]) -> str:
        if not cookies:
            return 'No cookies found.'
        headers = ['Name', 'Domain', 'Risk', 'Classification', 'Secure', 'Path']
        widths = [len(header) for header in headers]
        rows: List[List[str]] = []
        for cookie in cookies[:20]:
            row = [
                str(cookie.get('name', '')),
                str(cookie.get('domain', '')),
                str(cookie.get('risk', '')),
                str(cookie.get('classification', '')),
                'Y' if cookie.get('secure') else 'N',
                str(cookie.get('path', '')),
            ]
            rows.append(row)
            for index, cell in enumerate(row):
                widths[index] = max(widths[index], len(cell))
        lines = [' | '.join(label.ljust(widths[idx]) for idx, label in enumerate(headers))]
        lines.append('-' * (sum(widths) + 3 * (len(widths) - 1)))
        for row in rows:
            lines.append(' | '.join(cell.ljust(widths[idx]) for idx, cell in enumerate(row)))
        return '\n'.join(lines)

    def _json_payload(self, data: Dict) -> Dict:
        payload = data if 'targets' in data else {
            'cookies': data.get('cookies', []),
            'warnings': data.get('warnings', []),
            'count': len(data.get('cookies', [])),
        }
        payload['recommendations'] = self._recommendation_messages(data)
        return payload

    def _flatten_cookies(self, data: Dict) -> List[Dict]:
        if 'targets' in data:
            return [cookie for result in data['targets'] for cookie in result.get('cookies', [])]
        return data.get('cookies', [])

    def _recommendation_messages(self, data: Dict) -> List[str]:
        messages = set()
        for cookie in self._flatten_cookies(data):
            for reason in cookie.get('risk_reasons', []):
                if reason in RECOMMENDATIONS:
                    messages.add(RECOMMENDATIONS[reason])
        return sorted(messages)

    def _get_js_severity(self, match: Dict) -> str:
        keywords = [str(k).lower() for k in match.get('keywords', [])]
        if any(k in keywords for k in ('apikey', 'api_key', 'access_token', 'password', 'secret', 'token')):
            return 'High'
        if any(k in keywords for k in ('auth', 'session', 'cookie')):
            return 'Medium'
        if match.get('type') == 'document.cookie assignment':
            return 'Medium'
        return 'Low'

    def _render_match_snippet(self, snippet: str, keywords: List[str]) -> str:
        text = str(snippet or '').strip()
        if not text:
            return ''
        lower_text = text.lower()
        target = None
        for kw in keywords:
            kw = str(kw).lower()
            pos = lower_text.find(kw)
            if pos != -1:
                target = (pos, len(kw))
                break
        if target:
            start = max(0, target[0] - 50)
            end = min(len(text), target[0] + target[1] + 50)
        else:
            start = 0
            end = min(len(text), 120)
        snippet_text = text[start:end]
        if start > 0:
            snippet_text = '...' + snippet_text
        if end < len(text):
            snippet_text = snippet_text + '...'
        return html.escape(snippet_text)

    def _render_js_severity(self, severity: str) -> str:
        severity_key = str(severity or 'Low').lower()
        return f'<span class="severity severity-{severity_key}">{html.escape(str(severity))}</span>'

    def _escape(self, value: object) -> str:
        return html.escape(str(value))

    def _render_recommendations(self, data: Dict) -> str:
        messages = self._recommendation_messages(data)
        if not messages:
            return ''
        items = ''.join(f'<li>{message}</li>' for message in messages)
        return f'<section><h2>Recommendations</h2><p>Review the most important remediation guidance below:</p><ul>{items}</ul></section>'

    def _to_html(self, data: Dict) -> str:
        title = 'HexaCyberLab Cookie Inspector Pro Scan Report'
        hero = (
            '<section class="hero">'
            '<div><h1>Cookie Inspector Scan Report</h1>'
            '<p class="hero-copy">A consolidated dashboard view of cookie risk, JavaScript findings, and remediation actions, powered by an integrated HexaCyberLab engine.</p></div>'
            '<div><button class="btn" onclick="window.print()">Download PDF</button></div>'
            '</section>'
        )
        summary = self._render_summary(data)
        recommendations = self._render_recommendations(data)
        body = [hero, summary, recommendations]
        brand = '<div class="brand">HexaCyberLab Cookie Inspector Pro</div>'
        if 'targets' in data:
            for result in data['targets']:
                body.append(self._render_target_section(result))
        else:
            body.append(self._render_cookie_table(data.get('cookies', [])))
        return f'<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>{self._html_style()}</head><body><div class="report-shell">{brand}{"".join(body)}</div></body></html>'

    def _render_summary(self, data: Dict) -> str:
        total_targets = data.get('total_targets', 1)
        total_cookies = data.get('total_cookies', len(self._flatten_cookies(data)))
        warnings = len(data.get('warnings', []))
        critical = sum(1 for cookie in self._flatten_cookies(data) if cookie.get('risk') == 'Critical')
        high = sum(1 for cookie in self._flatten_cookies(data) if cookie.get('risk') == 'High')
        medium = sum(1 for cookie in self._flatten_cookies(data) if cookie.get('risk') == 'Medium')
        low = sum(1 for cookie in self._flatten_cookies(data) if cookie.get('risk') == 'Low')
        cards = [
            ('Targets', total_targets),
            ('Cookies', total_cookies),
            ('Warnings', warnings),
            ('Critical', critical),
            ('High', high),
            ('Medium', medium),
            ('Low', low),
        ]
        stats = ''.join(
            f'<div class="stat-card"><span>{label}</span><strong>{value}</strong></div>'
            for label, value in cards
        )
        return f'<section class="summary"><h2>Summary</h2><div class="stats-grid">{stats}</div></section>'

    def _render_cli_summary(self, data: Dict) -> str:
        targets = data.get('total_targets', 1)
        cookies = data.get('total_cookies', len(self._flatten_cookies(data)))
        warnings = len(data.get('warnings', []))
        pages = sum((result.get('summary', {}).get('pages', 0) for result in data.get('targets', []))) if 'targets' in data else 0
        critical = sum(1 for cookie in self._flatten_cookies(data) if cookie.get('risk') == 'Critical')
        high = sum(1 for cookie in self._flatten_cookies(data) if cookie.get('risk') == 'High')
        medium = sum(1 for cookie in self._flatten_cookies(data) if cookie.get('risk') == 'Medium')
        low = sum(1 for cookie in self._flatten_cookies(data) if cookie.get('risk') == 'Low')
        js_findings = sum(len(result.get('js_analysis', [])) for result in data.get('targets', [])) if 'targets' in data else len(data.get('js_analysis', []))
        lines = [
            '=== Cookie Inspector Summary ===',
            f'Targets scanned: {targets}',
            f'Pages crawled: {pages}',
            f'Cookies found: {cookies}',
            f'JS findings: {js_findings}',
            f'Warnings: {warnings}',
            f'Risk counts: Critical={critical} High={high} Medium={medium} Low={low}',
            '=================================' if targets or cookies or warnings else ''
        ]
        return '\n'.join(line for line in lines if line)

    def _render_target_section(self, result: Dict) -> str:
        header = f'<h2>Target: {self._escape(result.get("target", ""))}</h2>'
        warnings = result.get('warnings', [])
        warning_html = ''
        if warnings:
            warning_html = '<div class="warnings"><h3>Warnings</h3><ul>' + ''.join(f'<li>{self._escape(w)}</li>' for w in warnings) + '</ul></div>'
        summary = result.get('summary', {})
        stats = '<p>' + ', '.join(f'{key}: {value}' for key, value in summary.items() if key in {'found_cookies', 'pages'}) + '</p>'
        table = self._render_cookie_table(result.get('cookies', []))
        js_section = self._render_js_analysis(result.get('js_analysis', []))
        js_leaker_section = self._render_js_leaker_section(result.get('js_leaker', {}))
        return f'<section>{header}{warning_html}{stats}{table}{js_section}{js_leaker_section}</section>'

    def _render_cookie_table(self, cookies: List[Dict]) -> str:
        if not cookies:
            return '<p>No cookies found.</p>'
        palette = {'Critical': '#b91c1c', 'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#22c55e'}
        rows = ''.join(self._render_cookie_row(cookie, palette) for cookie in cookies)
        return f'<table><thead><tr><th>Name</th><th>Domain</th><th>Risk</th><th>Classification</th><th>Secure</th><th>HttpOnly</th><th>Path</th></tr></thead><tbody>{rows}</tbody></table>'

    def _render_js_analysis(self, js_analysis: List[Dict]) -> str:
        if not js_analysis:
            return '<section><h3>JS-Driven Cookie Analysis</h3><p>No suspicious JavaScript cookie logic or hardcoded secrets found.</p></section>'
        items = []
        for script in js_analysis:
            matches_html = []
            for match in script.get('matches', []):
                severity = self._get_js_severity(match)
                snippet = self._render_match_snippet(match.get('snippet', ''), match.get('keywords', []))
                keywords = ', '.join(match.get('keywords', []))
                match_line = (
                    '<li>'
                    f'<strong>Line {match.get("line")}</strong> '
                    f'(<span class="match-type">{match.get("type")}</span>) '
                    f'{self._render_js_severity(severity)}'
                    f'<br/><code>{snippet}</code>'
                )
                if keywords:
                    match_line += f'<br/><span class="match-keywords">Keywords: {html.escape(keywords)}</span>'
                match_line += '</li>'
                matches_html.append(match_line)
            items.append(
                f'<div class="js-script"><h4>Script: {html.escape(str(script.get("script_url", "unknown")))}</h4><ul>{"".join(matches_html)}</ul></div>'
            )
        return ('<section><h3>JS-Driven Cookie Analysis</h3>'
                '<p>JavaScript resources were scanned for cookie-setting logic and hardcoded secrets.</p>'
                f'{"".join(items)}'
                '</section>')

    def _render_js_leaker_section(self, js_leaker: Dict) -> str:
        if not js_leaker:
            return ''
        if js_leaker.get('error'):
            return ('<section><h3>Deep JS-Leaker Analysis</h3>'
                    f'<p>JS-Leaker execution failed: {js_leaker.get("error")}</p></section>')

        summary = js_leaker.get('summary', {})
        files = js_leaker.get('downloaded_files', [])
        findings = js_leaker.get('findings', [])
        details = []
        if summary:
            details.append(f'<p>Downloaded JS files: {summary.get("downloaded_files", len(files))}</p>')
            details.append(f'<p>JS-Leaker findings: {summary.get("findings", len(findings))}</p>')
        if findings:
            details.append('<ul>' + ''.join(
                f'<li><strong>{item.get("file")}</strong>: {len(item.get("findings", []))} findings</li>'
                for item in findings
            ) + '</ul>')
        return ('<section><h3>Deep JS-Leaker Analysis</h3>'
                '<p>JS-Leaker was invoked as an integrated HexaCyberLab engine to collect external and inline JavaScript assets for deeper analysis.</p>'
                + ''.join(details) + '</section>')

    def _render_cookie_row(self, cookie: Dict, palette: Dict[str, str]) -> str:
        risk = self._escape(cookie.get('risk', 'Low'))
        color = palette.get(risk, '#666')
        return ('<tr>'
                f'<td>{self._escape(cookie.get("name", ""))}</td>'
                f'<td>{self._escape(cookie.get("domain", ""))}</td>'
                f'<td style="color:{color};">{risk}</td>'
                f'<td>{self._escape(cookie.get("classification", ""))}</td>'
                f'<td>{"Yes" if cookie.get("secure") else "No"}</td>'
                f'<td>{"Yes" if cookie.get("httponly") else "No"}</td>'
                f'<td>{self._escape(cookie.get("path", ""))}</td>'
                '</tr>')

    def _html_style(self) -> str:
        return ('<style>body{font-family:Inter,system-ui,Segoe UI,Arial,sans-serif;background:#040713;color:#e2e8f0;padding:24px;line-height:1.6;margin:0;}'
                '.brand{font-size:1.1rem;font-weight:800;color:#38bdf8;margin-bottom:18px;letter-spacing:.08em;text-transform:uppercase;}'
                '.hero{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:24px;background:#071018;border:1px solid #334155;border-radius:18px;margin-bottom:22px;box-shadow:0 24px 56px rgba(15,23,42,.35);}'
                '.hero h1{margin:0;font-size:2rem;color:#f8fafc;} .hero-copy{margin:8px 0 0;color:#94a3b8;max-width:640px;}'
                '.btn{background:#38bdf8;color:#020617;border:none;border-radius:999px;padding:14px 22px;cursor:pointer;font-weight:700;box-shadow:0 12px 24px rgba(56,189,248,.24);transition:transform .2s ease,background .2s ease;}'
                '.btn:hover{transform:translateY(-1px);background:#22d3ee;}'
                '.summary{margin-bottom:20px;}'
                '.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-top:18px;}'
                '.stat-card{background:#0f172a;border:1px solid #334155;padding:18px;border-radius:16px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.03);}'
                '.stat-card strong{display:block;font-size:1.85rem;margin-top:10px;color:#f8fafc;} .stat-card span{font-size:.85rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;}'
                'section{background:#0f172a;border:1px solid #334155;border-radius:12px;padding:18px;margin-bottom:18px;box-shadow:0 16px 40px rgba(15,23,42,.25);}'
                'h2{margin:0 0 12px;color:#f8fafc;} table{width:100%;border-collapse:collapse;margin-top:18px;background:#0f172a;color:#e2e8f0;}'
                'th,td{border:1px solid #334155;padding:12px;text-align:left;} th{background:#1e293b;color:#f8fafc;} tr:nth-child(even){background:#111827;} tr:hover{background:#1e293b;}'
                'p,li{color:#cbd5e1;margin:6px 0;} ul{padding-left:20px;} a{color:#60a5fa;} .warnings{background:#1f2937;border:1px solid #475569;padding:14px;margin:14px 0;}'
                '.recommendations{margin-top:18px;} .recommendations h2{color:#38bdf8;}'
                '.report-shell{max-width:1280px;margin:0 auto;} .hero{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:24px;padding:24px 28px;background:#071018;border:1px solid #334155;border-radius:18px;margin-bottom:22px;box-shadow:0 24px 56px rgba(15,23,42,.35);}'
                '.hero h1{margin:0;font-size:2.1rem;color:#f8fafc;} .hero-copy{margin:8px 0 0;color:#94a3b8;max-width:680px;} .btn{background:#38bdf8;color:#020617;border:none;border-radius:999px;padding:14px 22px;cursor:pointer;font-weight:700;box-shadow:0 12px 24px rgba(56,189,248,.24);transition:transform .2s ease,background .2s ease;}'
                '.btn:hover{transform:translateY(-1px);background:#22d3ee;}'
                '@media print{.btn, .brand{display:none;}body{background:#fff;color:#000;}section{border:none;box-shadow:none;}}'
                '.js-script{margin-top:14px;padding:14px;border:1px solid #334155;border-radius:12px;background:#111827;}'
                '.js-script h4{margin:0 0 10px;color:#9f7aea;} .js-script li{margin-bottom:12px;}'
                '.match-type{color:#38bdf8;font-weight:600;} .severity{font-weight:700;padding:.15em .55em;border-radius:999px;margin-left:8px;font-size:.85rem;vertical-align:middle;}'
                '.severity-high{background:#991b1b;color:#fee2e2;} .severity-medium{background:#c2410c;color:#fff7ed;} .severity-low{background:#047857;color:#d1fae5;}'
                '.match-keywords{display:block;margin-top:6px;color:#a5b4fc;} code{display:block;padding:12px;margin-top:10px;background:#020617;border:1px solid #334155;border-radius:10px;color:#f8fafc;white-space:pre-wrap;word-break:break-word;}'
                '</style>')

    def _write_pdf(self, html: str, output: Path) -> None:
        try:
            import pdfkit
        except ImportError as exc:
            raise RuntimeError('PDF export requires pdfkit. Install with `pip install pdfkit` and a system wkhtmltopdf binary.') from exc
        pdfkit.from_string(html, str(output))


if __name__ == '__main__':
    test_data = {'cookies': [{'name': 'session', 'value': 'abc', 'domain': '.ex.com', 'path': '/', 'secure': True, 'httponly': True}], 'warnings': []}
    Reporter('table').generate(test_data)

