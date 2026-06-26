# scrape-smith

[![PyPI](https://img.shields.io/pypi/v/scrape-smith.svg)](https://pypi.org/project/scrape-smith/)
[![Python](https://img.shields.io/pypi/pyversions/scrape-smith.svg)](https://pypi.org/project/scrape-smith/)
[![GitHub](https://img.shields.io/badge/GitHub-yeiichi%2Fscrape--smith-181717?logo=github)](https://github.com/yeiichi/scrape-smith)

No-dependency Python utilities for scraping workflows.

The package exposes one main CLI command, `scrape`, with subcommands for each tool.

```bash
scrape tables <html-file-or-url>
```

The table tool extracts tables from a local HTML file or HTTP(S) URL and writes
the result to a file. CSV is the default output format, and successful commands
do not print table data to the screen.

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

Python APIs live under `scrape_smith.tools`.

```python
from scrape_smith.tools.tables import extract_tables

tables = extract_tables("page.html")
```
