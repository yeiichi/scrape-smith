from scrape_smith.tools.tables import extract_tables_from_html


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
