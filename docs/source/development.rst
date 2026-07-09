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

Read the Docs deployment is triggered from GitHub Actions instead of the
Read the Docs GitHub App. Configure the repository secret
``RTD_WEBHOOK_SECRET`` with the secret from the Read the Docs webhook
integration. The workflow sends a signed GitHub push webhook to Read the Docs
on pushes to ``main`` and can be run manually for another Git branch.

Documentation should describe the actual command-line behavior and Python API in
``src/scrape_smith``. When a new tool is added, update the CLI reference, add a
tool page, and include API coverage where the public functions are meant to be
used directly.
