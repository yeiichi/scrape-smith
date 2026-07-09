Development
===========

Set up the repository with uv:

.. code-block:: bash

   uv sync

Run the test suite:

.. code-block:: bash

   uv run pytest

Build the documentation locally:

.. code-block:: bash

   python -m pip install -r docs/requirements.txt
   sphinx-build -b html -E docs/source docs/build/html

If the local environment has locale-related Sphinx startup errors, retry with a
plain C locale:

.. code-block:: bash

   LC_ALL=C LANG=C sphinx-build -b html -E docs/source docs/build/html

Read the Docs builds the documentation from the repository using its project
configuration and ``.readthedocs.yaml``. Keep that file in sync with the local
documentation build requirements when dependencies or build settings change.
The Read the Docs project is configured to update only when files under
``docs`` change; that trigger rule is managed in Read the Docs, not in this
repository.

Documentation should describe the actual command-line behavior and Python API in
``src/scrape_smith``. When a new tool is added, update the CLI reference, add a
tool page, and include API coverage where the public functions are meant to be
used directly.
