# scrape-smith

[![PyPI](https://img.shields.io/pypi/v/scrape-smith.svg)](https://pypi.org/project/scrape-smith/)
[![Python](https://img.shields.io/pypi/pyversions/scrape-smith.svg)](https://pypi.org/project/scrape-smith/)
[![GitHub](https://img.shields.io/badge/GitHub-yeiichi%2Fscrape--smith-181717?logo=github)](https://github.com/yeiichi/scrape-smith)

No-dependency Python utilities for scraping workflows.

The package provides a `scrape` command with tools for table extraction, list
extraction, body content JSONL conversion, combined three-in-one extraction,
and polite file downloads.

## Installation

scrape-smith requires Python 3.10 or newer.

```bash
python -m pip install scrape-smith
```

## Quickstart

```bash
scrape tables <html-file-or-url>
```

```bash
scrape tables page.html
scrape tables https://example.com/page.html -o result.csv
scrape tables page.html --format json -o tables.json
```

Without `-o`, output is written to a safe source-based filename:

```text
page.html -> page-tables.csv
https://yeiichi.github.io/claim-class-model -> claim-class-model-tables.csv
```

If the default filename already exists, `scrape` avoids overwriting it by adding
a numeric suffix, such as `page-tables-2.csv`.

On success, `scrape` reports the written file to stdout:

```text
Wrote 1 table to page-tables.csv
```

Use `--quiet` to suppress the success report.

Extract lists from an HTML page:

```bash
scrape lists page.html
scrape lists https://example.com/page.html
```

The lists command reads a local HTML file or HTTP(S) URL and extracts `ul`,
`ol`, and `dl` elements. Ordered and unordered lists produce a single item
column in CSV. Definition lists produce two columns, `term` and `description`.
Multiple lists are separated by blank rows.

Without `-o`, CSV output is written to a safe source-based filename:

```text
page.html -> page-lists.csv
```

Convert body content from one HTML page to JSONL:

```bash
scrape content page.html
scrape content https://example.com/page.html
```

The content command reads a local HTML file or HTTP(S) URL, extracts visible
text from the `<body>`, ignores metadata-like elements such as `<script>`, and
writes one JSON object per line for headings (`h1`–`h6`), paragraphs (`p`), links (`a`), list items (`li`), table cells (`td`, `th`), block quotes (`blockquote`), figure captions (`figcaption`), definition terms and descriptions (`dt`, `dd`), table captions (`caption`), labels (`label`), and buttons (`button`):

```json
{"h1": "Title"}
{"p": "Hello docs."}
{"a": "docs", "href": "/docs"}
```

Without `-o`, JSONL output is written to a safe source-based filename:

```text
page.html -> page-content.jsonl
```

Extract all three in source order into one JSONL file:

```bash
scrape three page.html
scrape three https://example.com/page.html
```

The `three` command runs content, table, and list extraction in a single pass
and writes every record to one JSONL file in document order. Each line is a
`{"type": ..., "data": ...}` object where `data` is a JSON string:

```json
{"type": "content", "data": "{\"tag\": \"h1\", \"text\": \"Title\"}"}
{"type": "list",    "data": "{\"tag\": \"ul\", \"items\": [\"Alpha\", \"Beta\"]}"}
{"type": "table",   "data": "{\"caption\": null, \"headers\": [\"Name\"], \"rows\": [[\"Ada\"]]}"}
```

Without `-o`, output is written to a safe source-based filename:

```text
page.html -> page-extract.jsonl
```

Download target files from a URL list:

```bash
scrape download /path/to/urls.txt
```

The URL list should contain one URL per line. Blank lines and lines starting
with `#` are ignored. scrape-smith downloads CSV, PDF, DOCX, XLSX, and PPTX files
sequentially, waits between requests by default, and skips non-target URLs.

Without `-o`, files are saved under a collision-safe directory based on the URL
list filename:

```text
urls.txt -> urls-downloads/
```

Downloaded files keep their original filenames when the URL or response headers
provide one. If no filename is available, scrape-smith falls back to a fixed-width
epoch filename such as `1700000000123.pdf`.

Warning: treat downloaded files as untrusted. Scan them before opening, and do
not open files blindly; documents and spreadsheets can contain harmful content.

## Command Line

The command-line entry point is `scrape`.

```bash
scrape tables <html-file-or-url> [--format csv|json] [-o OUTPUT] [--index N] [--quiet]
scrape lists <html-file-or-url> [--format csv|json] [-o OUTPUT] [--quiet]
scrape content <html-file-or-url> [-o OUTPUT] [--quiet]
scrape three <html-file-or-url> [-o OUTPUT] [--quiet]
scrape download <url-list-path> [-o OUTPUT_DIR] [--delay SECONDS]
```

Options:

- `--format`: output format, either `csv` or `json`; defaults to `csv`
- `-o`, `--output`: output file path; defaults to a safe source-based filename
- `--index`: write one table by zero-based index
- `-q`, `--quiet`: suppress success reports on stdout

Download options:

- `-o`, `--output-dir`: output directory; defaults to a safe URL-list-based name
- `--delay`: seconds to wait between requests; defaults to `1`

Errors and validation messages are written to stderr. If `--index` is out of
range, the command exits with status code `2`.

## Python API

Python APIs live under `scrape_smith.tools`.

```python
from scrape_smith.tools.tables import extract_tables

tables = extract_tables("page.html")
```

Each extracted table has `caption`, `headers`, and `rows` fields. JSON output
uses the same shape.

```python
from scrape_smith.tools.downloads import download_files

summary = download_files("urls.txt", delay_seconds=1)
print(summary.downloaded_count)
```

```python
from scrape_smith.tools.lists import extract_lists

lists = extract_lists("page.html")
```

```python
from scrape_smith.tools.extract import extract_all

records = extract_all("page.html")
```

```python
from scrape_smith.tools.content import extract_content_records

records = extract_content_records("page.html")
```

## Documentation

Full documentation is available at <https://scrape-smith.readthedocs.io/>.
