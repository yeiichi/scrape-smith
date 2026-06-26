Command Line
============

The command-line entry point is ``scrape``.

.. code-block:: bash

   scrape <command> [options]

Currently, the available command is ``tables``.

``scrape tables``
-----------------

Extract tables from a local HTML file or an HTTP(S) URL.

.. code-block:: bash

   scrape tables <html-file-or-url> [--format csv|json] [-o OUTPUT] [--index N]

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

Examples
--------

.. code-block:: bash

   scrape tables page.html
   scrape tables page.html -o tables.csv
   scrape tables page.html --format json -o tables.json
   scrape tables page.html --index 0 -o first-table.csv
   scrape tables https://example.com/report.html -o report.csv

Successful commands write data to a file and do not print table data to stdout.
