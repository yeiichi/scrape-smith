Quickstart
==========

scrape-smith provides small, dependency-light tools for scraping workflows. The
first tool extracts HTML tables from local files or HTTP(S) pages.

Extract tables from a local HTML file:

.. code-block:: bash

   scrape tables page.html

By default, CSV output is written to a safe source-based filename:

.. code-block:: text

   page.html -> page-tables.csv

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
