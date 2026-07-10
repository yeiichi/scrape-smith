Three-in-One Extraction
=======================

The extract tool runs content, table, and list extraction in a single parser
pass and writes all records to one JSONL file in document order. It is designed
for pipelines that need the full structural context of a page — headings,
paragraphs, links, tables, and lists — without running separate commands.

Supported sources
-----------------

``extract_all`` and ``scrape three`` accept:

- a local HTML file path
- an HTTP or HTTPS URL

Output model
------------

Each record has exactly two top-level keys:

``type``
   One of ``"content"``, ``"table"``, or ``"list"``.

``data``
   A JSON string with the record payload.

This two-key envelope gives a consistent schema for BigQuery loading
(``type STRING, data STRING`` or ``data JSON``).

Content payload (``type: "content"``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {"tag": "h1", "text": "Title"}
   {"tag": "p",  "text": "Hello."}
   {"tag": "a",  "text": "docs", "href": "/docs"}

Covers ``h1``–``h6``, ``p``, ``a``, ``blockquote``, ``figcaption``,
``label``, and ``button``. Elements inside a table or list are not emitted as
separate content records.

Table payload (``type: "table"``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {"caption": "People", "headers": ["Name"], "rows": [["Ada"]]}

List payload (``type: "list"``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

   {"tag": "ul", "items": ["Alpha", "Beta"]}
   {"tag": "dl", "items": [{"term": "Python", "description": "A language."}]}

Record ordering
---------------

Records are emitted in document source order. A heading that precedes a table
in the HTML will appear before that table's record in the output.

Output filename
---------------

When no output path is supplied, scrape-smith writes to a safe filename based
on the source:

.. code-block:: text

   page.html -> page-extract.jsonl

If that filename already exists, a numeric suffix is added, such as
``page-extract-2.jsonl``.
