import json
from io import StringIO

from scrape_smith.tools.content import extract_content_records_from_html
from scrape_smith.tools.content import write_jsonl


def test_extract_content_records_from_body() -> None:
    html = """
    <html>
      <head>
        <title>Ignore me</title>
      </head>
      <body>
        <h1>Title</h1>
        <p>Hello <a href="/docs">docs</a>.</p>
        <h2>Next</h2>
      </body>
    </html>
    """

    records = extract_content_records_from_html(html)

    assert records == [
        {"h1": "Title"},
        {"p": "Hello docs."},
        {"a": "docs", "href": "/docs"},
        {"h2": "Next"},
    ]


def test_extract_content_records_ignores_metadata_like_elements() -> None:
    html = """
    <body>
      <h1>Visible</h1>
      <script><p>Hidden script</p></script>
      <style><p>Hidden style</p></style>
      <template><p>Hidden template</p></template>
      <noscript><p>Hidden noscript</p></noscript>
      <p>Visible paragraph</p>
    </body>
    """

    records = extract_content_records_from_html(html)

    assert records == [
        {"h1": "Visible"},
        {"p": "Visible paragraph"},
    ]


def test_extract_content_records_requires_body() -> None:
    html = """
    <h1>Outside body</h1>
    <p>Also outside body</p>
    """

    assert extract_content_records_from_html(html) == []


def test_extract_content_records_flushes_unclosed_body_elements() -> None:
    html = """
    <body>
      <p>Unclosed paragraph
    </body>
    """

    records = extract_content_records_from_html(html)

    assert records == [{"p": "Unclosed paragraph"}]


def test_write_jsonl() -> None:
    output = StringIO()

    write_jsonl([{"h1": "Title"}, {"a": "Docs", "href": "/docs"}], output)

    lines = output.getvalue().splitlines()
    assert [json.loads(line) for line in lines] == [
        {"h1": "Title"},
        {"a": "Docs", "href": "/docs"},
    ]
