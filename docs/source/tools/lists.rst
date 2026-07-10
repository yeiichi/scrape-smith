HTML List Extraction
====================

The list tool extracts ordered, unordered, and definition lists from HTML
pages and writes them to CSV or JSON.

Supported sources
-----------------

``extract_lists`` and ``scrape lists`` accept:

- a local HTML file path
- an HTTP or HTTPS URL

Supported list types
--------------------

+--------+--------------------------------------------------+
| Tag    | Description                                      |
+========+==================================================+
| ``ul`` | Unordered list — one item column in CSV          |
+--------+--------------------------------------------------+
| ``ol`` | Ordered list — one item column in CSV            |
+--------+--------------------------------------------------+
| ``dl`` | Definition list — ``term``/``description`` cols  |
+--------+--------------------------------------------------+

Nested lists are flattened: only the text of the outer list item is kept.

Output model
------------

Each list becomes one record:

- ``HtmlList`` for ``ul``/``ol`` — holds a flat ``items: list[str]``
- ``HtmlDefinitionList`` for ``dl`` — holds ``items: list[dict[str, str]]``
  where each dict has ``term`` and ``description`` keys

Example JSON output:

.. code-block:: json

   [
     {"tag": "ul", "items": ["Alpha", "Beta"]},
     {"tag": "dl", "items": [{"term": "Python", "description": "A language."}]}
   ]

Output filename
---------------

When no output path is supplied, scrape-smith writes to a safe filename based
on the source:

.. code-block:: text

   page.html -> page-lists.csv

If that filename already exists, a numeric suffix is added, such as
``page-lists-2.csv``.
