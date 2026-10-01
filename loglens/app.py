"""LogLens — local, dependency-free log inspector."""
import json
import re
from collections import Counter
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

LIMIT = 5 * 1024 * 1024
# Recognize a level at the start, after an ISO timestamp, or in brackets.
STAMP = r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?'
LEVEL = r'ERROR|FATAL|CRITICAL|WARNING|WARN|INFO|DEBUG'
PREFIX = re.compile(rf'^\s*(?:(?:\[{STAMP}\]|{STAMP})\s*)?(?:\[(?P<bracket>{LEVEL})\]|(?P<plain>{LEVEL})\b)\s*[:\-]?\s*', re.I)


def analyze(text):
    lines = text.lstrip('\ufeff').splitlines()
    if not lines or not any(line.strip() for line in lines):
        raise ValueError('The log file is empty.')
    if len(lines) > 50000:
        raise ValueError('Limit: 50,000 lines.')
    entries, counts, errors = [], Counter(), Counter()
    for number, line in enumerate(lines, 1):
        match = PREFIX.match(line)
        level = (match.group('bracket') or match.group('plain')).upper() if match else 'OTHER'
        level = {'WARN': 'WARNING', 'FATAL': 'ERROR', 'CRITICAL': 'ERROR'}.get(level, level)
        message = line[match.end():].strip() if match else line.strip()
        counts[level] += 1
        if level == 'ERROR':
            errors[message] += 1
        entries.append({'line': number, 'level': level, 'message': message, 'raw': line})
    return {'total_lines': len(lines), 'counts': {level: counts[level] for level in ['ERROR','WARNING','INFO','DEBUG','OTHER']},
            'error_groups': [{'message': msg, 'count': count} for msg, count in errors.most_common()], 'entries': entries}


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, kind):
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        names = {'/': ('index.html','text/html; charset=utf-8'), '/sample.log': ('sample.log','text/plain; charset=utf-8')}
        if self.path not in names:
            self.reply(404,b'Not found','text/plain')
            return
        name, kind = names[self.path]
        self.reply(200,Path(__file__).with_name(name).read_bytes(),kind)

    def do_POST(self):
        if self.path != '/analyze':
            self.reply(404,b'Not found','text/plain')
            return
        try:
            size = int(self.headers.get('Content-Length',0))
            if not 0 < size <= LIMIT:
                raise ValueError('Choose a UTF-8 log file up to 5 MB.')
            result = analyze(self.rfile.read(size).decode('utf-8'))
            self.reply(200,json.dumps(result).encode(),'application/json')
        except ValueError as error:
            self.reply(400,json.dumps({'error':str(error)}).encode(),'application/json')

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1',8001),Handler)
    print('LogLens running at http://localhost:8001 — Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nLogLens stopped.')
    finally:
        server.server_close()
