# scrape-smith

[![PyPI](https://img.shields.io/pypi/v/scrape-smith.svg)](https://pypi.org/project/scrape-smith/)
[![Python](https://img.shields.io/pypi/pyversions/scrape-smith.svg)](https://pypi.org/project/scrape-smith/)
[![GitHub](https://img.shields.io/badge/GitHub-yeiichi%2Fscrape--smith-181717?logo=github)](https://github.com/yeiichi/scrape-smith)

No-dependency Python utilities for scraping workflows.

The package currently provides a `scrape` command with a table extraction tool.
It can read HTML from a local file or HTTP(S) URL, extract tables, and write CSV
or JSON output to a file.

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

## Command Line

The command-line entry point is `scrape`.

```bash
scrape tables <html-file-or-url> [--format csv|json] [-o OUTPUT] [--index N] [--quiet]
```

Options:

- `--format`: output format, either `csv` or `json`; defaults to `csv`
- `-o`, `--output`: output file path; defaults to a safe source-based filename
- `--index`: write one table by zero-based index
- `-q`, `--quiet`: suppress success reports on stdout

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

## Documentation

Full documentation is available at <https://scrape-smith.readthedocs.io/>.
