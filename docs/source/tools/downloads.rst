File Downloads
==============

The download tool saves known document and data files from a URL list. It is
intentionally sequential and small: it does not crawl pages or open concurrent
requests.

Supported sources
-----------------

``download_files`` and ``scrape download`` accept a text file containing one URL
per line. Blank lines and lines starting with ``#`` are ignored.

Only HTTP and HTTPS URLs are downloaded. Other URL schemes are skipped.

Target files
------------

The supported target extensions are:

- ``.csv``
- ``.pdf``
- ``.docx``
- ``.xlsx``
- ``.pptx``

scrape-smith first checks the URL path and ``Content-Disposition`` filename. If
no filename is available, it can infer a target extension from common
``Content-Type`` values.

Output directory
----------------

When no output directory is supplied, scrape-smith creates a directory based on
the URL list filename:

.. code-block:: text

   urls.txt -> urls-downloads/

If that directory already exists, a numeric suffix is added, such as
``urls-downloads-2``.

Filenames
---------

Downloaded files keep their original filename when the URL path or response
headers provide one. Existing files are not overwritten; a numeric suffix is
added before the extension.

.. warning::

   Treat downloaded files as untrusted. Scan them before opening, and do not
   open files blindly; documents and spreadsheets can contain harmful content.

If no filename is available, scrape-smith uses a fixed-width epoch-millisecond
filename with the detected extension:

.. code-block:: text

   1700000000123.pdf

Request behavior
----------------

Downloads run one at a time. By default, the CLI waits one second between
requests. Use ``--delay`` to choose a longer or shorter delay.

The CLI prints important events to stdout: the start, output directory, safety
warning, each downloaded/skipped/failed URL, and the final summary. If any
download fails, scrape-smith finishes the remaining URLs and exits with status
code ``1``.
