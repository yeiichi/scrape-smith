Python API
==========

The public Python API currently lives under ``scrape_smith.tools``.

Table helpers
-------------

.. automodule:: scrape_smith.tools.tables
   :members: HtmlTable, extract_tables, extract_tables_from_html, read_html
   :undoc-members:
   :show-inheritance:

Download helpers
----------------

.. automodule:: scrape_smith.tools.downloads
   :members: DownloadResult, DownloadSummary, download_files, download_url, read_url_list
   :undoc-members:
   :show-inheritance:

CLI helpers
-----------

The CLI module is importable for tests and advanced integrations, but most
callers should use the ``scrape`` command directly.

.. automodule:: scrape_smith.cli
   :members:
   :undoc-members:
   :show-inheritance:
