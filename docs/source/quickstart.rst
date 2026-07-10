Quickstart
==========

scrape-smith provides small, dependency-light tools for scraping workflows.

Extract tables from a local HTML file:

.. code-block:: bash

   scrape tables page.html

By default, CSV output is written to a safe source-based filename:

.. code-block:: text

   page.html -> page-tables.csv

On success, the command reports what it wrote to stdout:

.. code-block:: text

   Wrote 1 table to page-tables.csv

Extract tables from a URL and choose the output file:

.. code-block:: bash

   scrape tables https://example.com/page.html -o result.csv

Write JSON instead of CSV:

.. code-block:: bash

   scrape tables page.html --format json -o tables.json

.. note::

   If the source contains multiple tables, the resulting CSV contains each table
   in order, separated by blank rows.

JSON output preserves each table as a separate object with ``caption``,
``headers``, and ``rows`` fields.

Use the Python API when a script needs table objects instead of files:

.. code-block:: python

   from scrape_smith.tools.tables import extract_tables

   tables = extract_tables("page.html")
   first_table = tables[0]

   print(first_table.headers)
   print(first_table.rows)

Extract lists from an HTML page:

.. code-block:: bash

   scrape lists page.html

The lists command extracts ``ul``, ``ol``, and ``dl`` elements. Ordered and
unordered lists produce a single item column in CSV. Definition lists produce
two columns, ``term`` and ``description``:

.. code-block:: text

   Alpha
   Beta

By default, CSV output is written to a safe source-based filename:

.. code-block:: text

   page.html -> page-lists.csv

Use the Python API when a script needs the list objects directly:

.. code-block:: python

   from scrape_smith.tools.lists import extract_lists

   lists = extract_lists("page.html")

Convert body content from one HTML page to JSONL:

.. code-block:: bash

   scrape content page.html

The content command extracts text from headings, paragraphs, links, list items,
table cells, block quotes, figure captions, definition lists, labels, and
buttons inside the ``body`` element, then writes one JSON object per line:

.. code-block:: json

   {"h1": "Title"}
   {"p": "Hello docs."}
   {"a": "docs", "href": "/docs"}

By default, JSONL output is written to a safe source-based filename:

.. code-block:: text

   page.html -> page-content.jsonl

Use the Python API when a script needs the records directly:

.. code-block:: python

   from scrape_smith.tools.content import extract_content_records

   records = extract_content_records("page.html")

Extract all three in source order into one JSONL file:

.. code-block:: bash

   scrape three page.html

The ``three`` command runs a single parser pass and writes every content
element, table, and list as a ``{"type": ..., "data": ...}`` record, preserving
document order:

.. code-block:: json

   {"type": "content", "data": "{\"tag\": \"h1\", \"text\": \"Title\"}"}
   {"type": "list",    "data": "{\"tag\": \"ul\", \"items\": [\"Alpha\"]}"}
   {"type": "table",   "data": "{\"caption\": null, \"headers\": [\"Name\"], \"rows\": [[\"Ada\"]]}"}

By default, output is written to a safe source-based filename:

.. code-block:: text

   page.html -> page-extract.jsonl

Use the Python API when a script needs the records directly:

.. code-block:: python

   from scrape_smith.tools.extract import extract_all

   records = extract_all("page.html")

Download files from a URL list:

.. code-block:: bash

   scrape download urls.txt

The downloader saves CSV, PDF, DOCX, XLSX, and PPTX files in a directory based on
the URL list name:

.. code-block:: text

   urls.txt -> urls-downloads/

It downloads sequentially, waits between requests by default, skips non-target
URLs, and prints start/end plus per-URL events to stdout.

.. warning::

   Treat downloaded files as untrusted. Scan them before opening, and do not
   open files blindly; documents and spreadsheets can contain harmful content.

Use the Python API when a script needs the download summary:

.. code-block:: python

   from scrape_smith.tools.downloads import download_files

   summary = download_files("urls.txt")
   print(summary.downloaded_count)
