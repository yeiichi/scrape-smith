Command Line
============

The command-line entry point is ``scrape``.

.. code-block:: bash

   scrape <command> [options]

The available commands are ``tables``, ``content``, and ``download``.

``scrape tables``
-----------------

Extract tables from a local HTML file or an HTTP(S) URL.

.. code-block:: bash

   scrape tables <html-file-or-url> [--format csv|json] [-o OUTPUT] [--index N] [--quiet]

Arguments and options:

``target``
   Local HTML file path or HTTP(S) URL.

``--format``
   Output format. Supported values are ``csv`` and ``json``. The default is
   ``csv``.

``-o``, ``--output``
   Output file path. When omitted, scrape-smith writes to a safe filename based
   on the source, such as ``page-tables.csv``.

``--index``
   Write only one table by zero-based index. If the index does not exist, the
   command exits with status code ``2`` and prints an error to stderr.

``-q``, ``--quiet``
   Suppress success reports on stdout.

Examples
--------

.. code-block:: bash

   scrape tables page.html
   scrape tables page.html -o tables.csv
   scrape tables page.html --format json -o tables.json
   scrape tables page.html --quiet
   scrape tables page.html --index 0 -o first-table.csv
   scrape tables https://example.com/report.html -o report.csv

Successful commands write table data to a file and print a short report to
stdout, such as ``Wrote 1 table to page-tables.csv``. Use ``--quiet`` to
suppress that report. Errors and validation messages are written to stderr.

``scrape content``
------------------

Convert visible HTML body content from one page to JSONL.

.. code-block:: bash

   scrape content <html-file-or-url> [-o OUTPUT] [--quiet]

Arguments and options:

``target``
   Local HTML file path or HTTP(S) URL.

``-o``, ``--output``
   Output JSONL file path. When omitted, scrape-smith writes to a safe filename
   based on the source, such as ``page-content.jsonl``.

``-q``, ``--quiet``
   Suppress success reports on stdout.

The content command reads text from the ``body`` element, skips metadata-like
elements such as ``script``, ``style``, ``template``, and ``noscript``, and
writes one JSON object per line for ``h1`` through ``h6``, ``p``, and ``a``
elements. Link records include ``href`` when present.

Examples
--------

.. code-block:: bash

   scrape content page.html
   scrape content page.html -o content.jsonl
   scrape content https://example.com/page.html

Example JSONL output:

.. code-block:: json

   {"h1": "Title"}
   {"p": "Hello docs."}
   {"a": "docs", "href": "/docs"}

``scrape download``
-------------------

Download target files from a text file containing one URL per line.

.. code-block:: bash

   scrape download <url-list-path> [-o OUTPUT_DIR] [--delay SECONDS]

Arguments and options:

``url_list``
   Text file containing one URL per line. Blank lines and lines starting with
   ``#`` are ignored.

``-o``, ``--output-dir``
   Output directory. When omitted, scrape-smith creates a safe directory name
   based on the URL list file, such as ``urls-downloads``.

``--delay``
   Seconds to wait between requests. The default is ``1``.

Target files are CSV, PDF, DOCX, XLSX, and PPTX. scrape-smith downloads URLs
sequentially, keeps original filenames when possible, avoids overwriting
existing files, and skips non-target URLs.

.. warning::

   Treat downloaded files as untrusted. Scan them before opening, and do not
   open files blindly; documents and spreadsheets can contain harmful content.

Examples
--------

.. code-block:: bash

   scrape download urls.txt
   scrape download urls.txt -o files
   scrape download urls.txt --delay 2

Successful commands print important events to stdout, including the start,
output directory, safety warning, each downloaded/skipped/failed URL, and the
final summary. If any download fails, the command finishes the list and exits
with status code ``1``.
