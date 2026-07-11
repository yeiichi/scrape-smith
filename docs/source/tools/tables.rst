Table Extraction
================

The table tool reads HTML and returns a list of table objects. It is intentionally
small and uses Python's standard library HTML parser.

Supported sources
-----------------

``extract_tables`` and ``scrape tables`` accept:

- a local HTML file path
- an HTTP or HTTPS URL

Remote requests use a ``scrape-smith/<version>`` user agent and a 30-second timeout.
HTML bytes are decoded with charset hints from byte-order marks, HTTP headers,
and HTML metadata. When no charset can be determined, scrape-smith tries UTF-8
and common Japanese encodings before falling back to replacement characters.

Output model
------------

Each extracted table is represented as ``HtmlTable``:

``caption``
   The table caption text, or ``None`` when no caption exists.

``headers``
   The first row when every cell in that row is a ``th`` element.

``rows``
   Data rows as a list of string lists.

Text is normalized by collapsing whitespace inside each cell.

Header behavior
---------------

Only the first all-``th`` row is treated as the column header row. Later rows
that mix ``th`` and ``td`` cells stay in ``rows``. This keeps row-header tables
usable without silently dropping data.

Nested tables
-------------

Nested table content is ignored for the outer table result. If a cell contains a
nested table, the outer cell is emitted from the outer table's own text content.

CSV and JSON output
-------------------

CSV output writes headers first when present, then rows. Multiple tables are
written into one CSV file separated by a blank row.

JSON output writes a list of objects:

.. code-block:: json

   [
     {
       "caption": "People",
       "headers": ["Name"],
       "rows": [["Ada"]]
     }
   ]
