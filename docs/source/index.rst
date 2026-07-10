scrape-smith
============

scrape-smith is a small collection of no-dependency Python utilities for
scraping workflows.

The package provides a ``scrape`` command with tools for table extraction, list
extraction, body content JSONL conversion, combined three-in-one extraction,
and polite file downloads.

.. code-block:: bash

   scrape tables page.html
   scrape tables https://example.com/page.html -o result.csv
   scrape tables page.html --format json -o tables.json
   scrape lists page.html
   scrape content page.html
   scrape three page.html
   scrape download urls.txt

The Python API exposes the same behavior for scripts and automation.

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
   tools/lists
   tools/content
   tools/extract
   tools/downloads

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
