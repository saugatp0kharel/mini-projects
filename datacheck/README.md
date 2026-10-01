# DataCheck — CSV Data Quality Inspector

A local web app that helps students and ML developers inspect datasets before training a model. Built with Python's standard library and vanilla JavaScript. No dependencies or API keys.

## Run on Mac

Install Python 3 if needed. Open this folder in VS Code, open its terminal, and run:

```bash
python3 app.py
```

Open **http://localhost:8000** in your browser. Click **Try demo**, or upload a UTF-8 CSV. Press Ctrl+C in the terminal to stop.

## Features

- Counts rows, columns, missing cells, and duplicate rows.
- Calculates completeness and missing-value percentages per column.
- Identifies problematic CSV record numbers.
- Previews cleaned data and downloads a cleaned CSV.
- Exports a structured JSON quality report.
- Rejects malformed CSV, duplicate/empty headers, and inconsistent row widths.
- Local processing: no external services and no uploaded files saved to disk.

## Demo in 30 seconds

1. Click Try demo: 6 rows, 4 columns, 3 missing cells, 1 duplicate, 87.5% completeness.
2. Explain that the Alice record contains spaces and repeats an existing row.
3. Inspect the problem records and cleaned preview.
4. Download cleaned CSV: 5 rows; blanks are retained rather than guessed.

## How it works

The browser sends CSV text to POST /analyze. Python's csv parser reads quoted and multiline fields. A pass over the records checks missing values and whitespace. A set of normalized row tuples detects duplicates. The server sends JSON metrics and cleaned CSV back to the browser. User-provided values are rendered with textContent.

Completeness = nonempty cells / total cells × 100. Duplicate detection occurs after trimming whitespace. Missing means an empty or whitespace-only cell; strings such as NA, null, and 0 are not treated as missing. Cleaning is user initiated through download; it does not change the original file.

Limits: 5 MB, 50,000 data rows, 100 columns, first 1,000 findings displayed/exported, first 20 cleaned rows previewed. Comma-separated UTF-8 only. This is a local prototype, not a production upload service. CSV content can contain spreadsheet formulas; review untrusted downloads before opening in a spreadsheet. It does not validate business rules, numeric types, outliers, or model readiness.

## Verify

```bash
python3 -m unittest -v
```

## One-hour learning and portfolio plan

- 0–10 min: run the app and demo.
- 10–25 min: read analyze() and change the sample data.
- 25–40 min: understand browser fetch, tables, and downloads.
- 40–50 min: run tests and try your own dataset.
- 50–60 min: take a screenshot and upload this folder to a GitHub repository named datacheck.

## Resume bullet — after running and understanding it

Developed a Python and JavaScript CSV quality inspector that detects missing values, whitespace issues, and duplicate records, with per-column completeness metrics and downloadable cleaning reports.

Only claim features and work you can explain. Do not claim accuracy improvements or time savings without measuring them.

## Suggested next feature

Add user-defined rules such as age between 0 and 120; report violations without automatically changing values.
