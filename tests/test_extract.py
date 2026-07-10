import json

from scrape_smith.tools.extract import extract_all_from_html


def _data(record: dict[str, str]) -> dict:
    return json.loads(record["data"])


def test_extracts_content_records() -> None:
    html = "<body><h1>Title</h1><p>Hello <a href='/docs'>docs</a>.</p></body>"
    records = extract_all_from_html(html)

    assert [r["type"] for r in records] == ["content", "content", "content"]
    assert _data(records[0]) == {"tag": "h1", "text": "Title"}
    assert _data(records[1]) == {"tag": "p", "text": "Hello docs."}
    assert _data(records[2]) == {"tag": "a", "text": "docs", "href": "/docs"}


def test_extracts_table_record() -> None:
    html = """
    <body>
      <table>
        <tr><th>Name</th><th>Role</th></tr>
        <tr><td>Ada</td><td>Engineer</td></tr>
      </table>
    </body>
    """
    records = extract_all_from_html(html)

    assert len(records) == 1
    assert records[0]["type"] == "table"
    assert _data(records[0]) == {
        "caption": None,
        "headers": ["Name", "Role"],
        "rows": [["Ada", "Engineer"]],
    }


def test_extracts_list_record() -> None:
    html = "<body><ul><li>Alpha</li><li>Beta</li></ul></body>"
    records = extract_all_from_html(html)

    assert len(records) == 1
    assert records[0]["type"] == "list"
    assert _data(records[0]) == {"tag": "ul", "items": ["Alpha", "Beta"]}


def test_preserves_source_order() -> None:
    html = """
    <body>
      <h1>Intro</h1>
      <ul><li>Item A</li></ul>
      <p>Middle</p>
      <table><tr><th>Col</th></tr><tr><td>Val</td></tr></table>
      <p>End</p>
    </body>
    """
    records = extract_all_from_html(html)

    assert [r["type"] for r in records] == [
        "content", "list", "content", "table", "content"
    ]
    assert _data(records[0]) == {"tag": "h1", "text": "Intro"}
    assert _data(records[1])["tag"] == "ul"
    assert _data(records[2]) == {"tag": "p", "text": "Middle"}
    assert records[3]["type"] == "table"
    assert _data(records[4]) == {"tag": "p", "text": "End"}


def test_content_inside_table_is_not_duplicated() -> None:
    html = "<body><table><tr><td><p>Cell text</p></td></tr></table></body>"
    records = extract_all_from_html(html)

    # only one table record — no separate content record for the <p>
    assert len(records) == 1
    assert records[0]["type"] == "table"


def test_content_inside_list_is_not_duplicated() -> None:
    html = "<body><ul><li><strong>Bold item</strong></li></ul></body>"
    records = extract_all_from_html(html)

    assert len(records) == 1
    assert records[0]["type"] == "list"
    assert _data(records[0])["items"] == ["Bold item"]


def test_data_values_are_json_strings() -> None:
    html = "<body><h1>Hi</h1></body>"
    records = extract_all_from_html(html)

    assert isinstance(records[0]["data"], str)
    # round-trip
    assert json.loads(records[0]["data"]) == {"tag": "h1", "text": "Hi"}


def test_ignored_tags_are_skipped() -> None:
    html = "<body><script>bad</script><h1>Good</h1></body>"
    records = extract_all_from_html(html)

    assert len(records) == 1
    assert _data(records[0])["text"] == "Good"


def test_empty_html_returns_empty() -> None:
    assert extract_all_from_html("<body></body>") == []
