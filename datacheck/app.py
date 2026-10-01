"""DataCheck: dependency-free, local CSV quality inspector."""
import csv
import io
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

LIMIT = 5 * 1024 * 1024

def analyze(text):
    records = list(csv.reader(io.StringIO(text.lstrip('\ufeff')), strict=True))
    if not records or not records[0]:
        raise ValueError('CSV must contain a header row.')
    headers = records[0]
    if any(not h.strip() for h in headers) or len(set(h.strip() for h in headers)) != len(headers):
        raise ValueError('Column names must be nonempty and unique after trimming.')
    rows = records[1:]
    if not rows:
        raise ValueError('CSV must contain at least one data row.')
    if len(rows) > 50000 or len(headers) > 100:
        raise ValueError('Limit: 50,000 rows and 100 columns.')
    issues, cleaned, seen = [], [], set()
    missing = [0] * len(headers)
    duplicates = 0
    for number, row in enumerate(rows, 2):
        if len(row) != len(headers):
            raise ValueError(f'CSV record {number} has {len(row)} fields; expected {len(headers)}.')
        trimmed = [v.strip() for v in row]
        for col, value in enumerate(trimmed):
            if not value:
                missing[col] += 1
                issues.append({'record': number, 'column': headers[col], 'issue': 'Missing value'})
            elif value != row[col]:
                issues.append({'record': number, 'column': headers[col], 'issue': 'Extra whitespace'})
        key = tuple(trimmed)
        if key in seen:
            duplicates += 1
            issues.append({'record': number, 'column': 'Entire row', 'issue': 'Duplicate after trimming'})
        else:
            seen.add(key)
            cleaned.append(trimmed)
    out = io.StringIO(newline='')
    writer = csv.writer(out)
    writer.writerow([h.strip() for h in headers])
    writer.writerows(cleaned)
    return {'rows': len(rows), 'columns': len(headers), 'missing_cells': sum(missing),
            'duplicates': duplicates, 'cleaned_rows': len(cleaned),
            'completeness': round(100 * (1 - sum(missing) / (len(rows) * len(headers))), 1),
            'column_summary': [{'column': h, 'missing': n, 'missing_percent': round(n / len(rows) * 100, 1)} for h, n in zip(headers, missing)],
            'issues': issues[:1000], 'total_issues': len(issues), 'headers': headers,
            'preview': cleaned[:20], 'cleaned_csv': out.getvalue()}

class Handler(BaseHTTPRequestHandler):
    def reply(self, code, data, content_type):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == '/':
            self.reply(200, Path(__file__).with_name('index.html').read_bytes(), 'text/html; charset=utf-8')
        elif self.path == '/sample.csv':
            self.reply(200, Path(__file__).with_name('sample.csv').read_bytes(), 'text/csv; charset=utf-8')
        else:
            self.reply(404, b'Not found', 'text/plain')

    def do_POST(self):
        if self.path != '/analyze':
            self.reply(404, b'Not found', 'text/plain')
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= LIMIT:
                raise ValueError('Upload a UTF-8 CSV smaller than 5 MB.')
            result = analyze(self.rfile.read(length).decode('utf-8'))
            self.reply(200, json.dumps(result).encode(), 'application/json')
        except (ValueError, csv.Error) as error:
            self.reply(400, json.dumps({'error': str(error)}).encode(), 'application/json')

if __name__ == '__main__':
    print('DataCheck running at http://localhost:8000 — Ctrl+C to stop')
    HTTPServer(('127.0.0.1', 8000), Handler).serve_forever()
