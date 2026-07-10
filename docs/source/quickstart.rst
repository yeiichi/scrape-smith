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
