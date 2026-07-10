HTML Content JSONL
==================

The content tool converts visible body content from one HTML page into JSONL.
It is intended for lightweight text extraction where preserving the order of
headings, paragraphs, and links matters more than reproducing the full DOM.

Supported sources
-----------------

``extract_content_records`` and ``scrape content`` accept:

- a local HTML file path
- an HTTP or HTTPS URL

Body-only extraction
--------------------

Only content between ``<body>`` and ``</body>`` is considered. Metadata-like
elements are ignored, including:

- ``script``
- ``style``
- ``template``
- ``noscript``

Output model
------------

The parser emits one JSON object per selected element:

- ``h1`` through ``h6`` records use the heading tag as the key
- ``p`` records use ``p`` as the key
- ``a`` records use ``a`` as the key and include ``href`` when present
- ``li``, ``td``, ``th``, ``blockquote``, ``figcaption``, ``dt``, ``dd``,
  ``caption``, ``label``, and ``button`` records use the element tag as the key

Example output:

.. code-block:: json

   {"h1": "Title"}
   {"p": "Hello docs."}
   {"a": "docs", "href": "/docs"}
   {"li": "First item"}
   {"td": "Cell value"}
   {"button": "Submit"}

Output filename
---------------

When no output path is supplied, scrape-smith writes to a safe filename based on
the source:

.. code-block:: text

   page.html -> page-content.jsonl

If that filename already exists, a numeric suffix is added, such as
``page-content-2.jsonl``.
