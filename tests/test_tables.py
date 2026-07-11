from scrape_smith.tools.tables import decode_html
from scrape_smith.tools.tables import extract_tables_from_html


def test_decode_html_uses_meta_charset_for_shift_jis() -> None:
    html = (
        '<html><head><meta charset="Shift_JIS"></head>'
        "<body><table><tr><td>日本語</td></tr></table></body></html>"
    ).encode("cp932")

    assert "日本語" in decode_html(html)


def test_decode_html_uses_header_charset() -> None:
    html = (
        '<html><head><meta charset="utf-8"></head>'
        "<body><table><tr><td>日本語</td></tr></table></body></html>"
    ).encode("utf-8")

    assert "日本語" in decode_html(html, header_charset="utf-8")


def test_decode_html_uses_utf8_bom() -> None:
    html = "\ufeff<html><body><table><tr><td>日本語</td></tr></table></body></html>"

    assert "日本語" in decode_html(html.encode("utf-8-sig"))


def test_extract_tables_from_html() -> None:
    html = """
    <table>
      <caption>People</caption>
      <tr><th>Name</th><th>Role</th></tr>
      <tr><td>Ada</td><td>Engineer</td></tr>
      <tr><td>Grace</td><td>Admiral</td></tr>
    </table>
    """

    tables = extract_tables_from_html(html)

    assert len(tables) == 1
    assert tables[0].caption == "People"
    assert tables[0].headers == ["Name", "Role"]
    assert tables[0].rows == [["Ada", "Engineer"], ["Grace", "Admiral"]]


def test_extract_tables_ignores_nested_table_text_for_outer_result() -> None:
    html = """
    <table>
      <tr>
        <td>Outer</td>
        <td><table><tr><td>Nested</td></tr></table></td>
      </tr>
    </table>
    """

    tables = extract_tables_from_html(html)

    assert len(tables) == 1
    assert tables[0].rows == [["Outer", ""]]


def test_extract_tables_keeps_row_headers_in_rows() -> None:
    html = """
    <table>
      <tr><th>Year</th><th>Total</th></tr>
      <tr><th>2026</th><td>42</td></tr>
    </table>
    """

    tables = extract_tables_from_html(html)

    assert tables[0].headers == ["Year", "Total"]
    assert tables[0].rows == [["2026", "42"]]
