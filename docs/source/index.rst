scrape-smith
============

scrape-smith is a small collection of no-dependency Python utilities for
scraping workflows.

The package currently provides a ``scrape`` command with a table extraction
tool. It can read HTML from a local file or HTTP(S) URL, extract tables, and
write CSV or JSON output without printing scraped table data to the terminal.

.. code-block:: bash

   scrape tables page.html
   scrape tables https://example.com/page.html -o result.csv
   scrape tables page.html --format json -o tables.json

The Python API exposes the same table extraction behavior for scripts and
automation.

Getting Started
---------------

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   cli

Tools
-----

.. toctree::
   :maxdepth: 1

   tools/tables

Python API
----------

.. toctree::
   :maxdepth: 2

   python-api

Development
-----------

.. toctree::
   :maxdepth: 2

   development
