# LogLens — Server Log Inspector

A local debugging tool built with Python's standard library and vanilla JavaScript. Upload a log, inspect severity counts, group repeated errors, search the original lines, and export findings.

## Run on Mac

Open the loglens folder in VS Code and run in its terminal:

```bash
python3 app.py
```

Open **http://localhost:8001** and click **Try demo**. No extra packages or API keys. Port 8001 lets DataCheck run at the same time on port 8000. Ctrl+C stops the server.

## Features

- Upload UTF-8 .log or .txt files (5 MB, 50,000 lines maximum).
- Count ERROR, WARNING, INFO, DEBUG, and OTHER lines.
- Normalize WARN to WARNING, and FATAL/CRITICAL to ERROR.
- Rank repeated errors by their exact message after prefix removal.
- Search original log text and filter by severity.
- View original line numbers with pagination (100 results per page).
- Download an overall JSON summary or all currently matching log lines.
- In-memory local processing; uploaded files are not saved.

## Supported formats

```text
2026-10-01 09:01:00 ERROR Database connection failed
2026-10-01T09:01:00.123Z [ERROR] Database connection failed
[2026-10-01T09:01:00Z] [ERROR] Database connection failed
ERROR: Database connection failed
```

The parser recognizes a severity at the beginning, optionally preceded by an ISO-style timestamp. It does not count the word ERROR inside an INFO message as an error. Blank lines and unrecognized formats are OTHER. Stack-trace continuation lines remain separate OTHER lines. JSON logs and custom prefixes are not parsed. Error grouping does not remove IDs or numbers from messages, so different request IDs produce different groups. The UI displays the top 50 groups; JSON includes all groups.

## Demo

The sample has **16 lines**: **5 errors**, **3 warnings**, **5 info**, **2 debug**, and **1 other**. Database connection failed appears 3 times; Payment service timeout appears twice. Search database and filter ERROR to see its 3 original lines. Download matching lines to preserve this evidence.

## Architecture

Browser uploads plain text to POST /analyze. Python regular expressions recognize prefixes, and collections.Counter aggregates severities and error messages. JSON carries results back to the page. JavaScript filters the records and renders values using textContent. No external services are called.

This is a local prototype, not a production server or an automatic root-cause detector. It reports log patterns; it cannot establish why a failure happened. Reports and matching-line exports can contain sensitive log content; review before sharing.

## Tests

```bash
python3 -m unittest -v
```

## Explain it in an interview

“I built LogLens to make long server logs easier to inspect. It parses common severity prefixes, groups repeated error messages, and lets users search and export the exact matching lines. I used Python for parsing and an HTTP API, with JavaScript for interactive filtering.”

## Resume bullet

Built a Python and JavaScript log inspection tool with severity classification, repeated-error aggregation, searchable line-level evidence, and downloadable debugging summaries.

## Next improvement

Add a user-configurable parser for custom log formats, or support structured JSON logs.
