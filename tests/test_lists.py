import csv
import json
from io import StringIO

import pytest

from scrape_smith.cli import default_lists_output_path
from scrape_smith.cli import main
from scrape_smith.tools.lists import HtmlDefinitionList
from scrape_smith.tools.lists import HtmlList
from scrape_smith.tools.lists import extract_lists_from_html


# --- extract_lists_from_html ---


def test_extract_ul() -> None:
    html = "<ul><li>Alpha</li><li>Beta</li></ul>"
    assert extract_lists_from_html(html) == [HtmlList(tag="ul", items=["Alpha", "Beta"])]


def test_extract_ol() -> None:
    html = "<ol><li>First</li><li>Second</li></ol>"
    assert extract_lists_from_html(html) == [HtmlList(tag="ol", items=["First", "Second"])]


def test_extract_dl() -> None:
    html = "<dl><dt>Term</dt><dd>Description</dd></dl>"
    assert extract_lists_from_html(html) == [
        HtmlDefinitionList(items=[{"term": "Term", "description": "Description"}])
    ]


def test_extract_multiple_lists() -> None:
    html = "<ul><li>A</li></ul><ol><li>1</li></ol>"
    assert extract_lists_from_html(html) == [
        HtmlList(tag="ul", items=["A"]),
        HtmlList(tag="ol", items=["1"]),
    ]


def test_extract_empty_list_items_are_skipped() -> None:
    html = "<ul><li>  </li><li>Item</li></ul>"
    assert extract_lists_from_html(html) == [HtmlList(tag="ul", items=["Item"])]


def test_nested_list_items_are_flattened_to_outer() -> None:
    html = "<ul><li>Outer <ul><li>Inner</li></ul></li></ul>"
    result = extract_lists_from_html(html)
    assert result == [HtmlList(tag="ul", items=["Outer"])]


def test_dl_dt_without_dd_gets_empty_description() -> None:
    html = "<dl><dt>Lonely term</dt></dl>"
    assert extract_lists_from_html(html) == [
        HtmlDefinitionList(items=[{"term": "Lonely term", "description": ""}])
    ]


def test_li_with_inline_elements_collects_all_text() -> None:
    html = "<ul><li><code>rg</code> — fast <strong>grep</strong></li></ul>"
    assert extract_lists_from_html(html) == [HtmlList(tag="ul", items=["rg — fast grep"])]


def test_extract_returns_empty_for_no_lists() -> None:
    html = "<p>No lists here</p>"
    assert extract_lists_from_html(html) == []


# --- CLI: scrape lists ---


def test_lists_command_writes_csv_by_default(tmp_path, monkeypatch, capsys) -> None:
    html_path = tmp_path / "page.html"
    html_path.write_text("<ul><li>Alpha</li><li>Beta</li></ul>", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    exit_code = main(["lists", str(html_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "Wrote 1 list to page-lists.csv\n"
    assert captured.err == ""
    with (tmp_path / "page-lists.csv").open(encoding="utf-8", newline="") as f:
        assert list(csv.reader(f)) == [["Alpha"], ["Beta"]]


def test_lists_command_writes_dl_csv_with_headers(tmp_path, capsys) -> None:
    html_path = tmp_path / "page.html"
    output_path = tmp_path / "out.csv"
    html_path.write_text(
        "<dl><dt>Term</dt><dd>Desc</dd></dl>", encoding="utf-8"
    )

    exit_code = main(["lists", str(html_path), "-o", str(output_path)])

    assert exit_code == 0
    with output_path.open(encoding="utf-8", newline="") as f:
        assert list(csv.reader(f)) == [["term", "description"], ["Term", "Desc"]]


def test_lists_command_writes_json(tmp_path, capsys) -> None:
    html_path = tmp_path / "page.html"
    output_path = tmp_path / "out.json"
    html_path.write_text("<ul><li>A</li></ul>", encoding="utf-8")

    exit_code = main(["lists", str(html_path), "--format", "json", "-o", str(output_path)])

    assert exit_code == 0
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data == [{"tag": "ul", "items": ["A"]}]


def test_lists_command_quiet(tmp_path, monkeypatch, capsys) -> None:
    html_path = tmp_path / "page.html"
    html_path.write_text("<ul><li>X</li></ul>", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    exit_code = main(["lists", str(html_path), "--quiet"])

    assert exit_code == 0
    assert capsys.readouterr().out == ""


def test_default_lists_output_path_avoids_overwriting(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "page-lists.csv").write_text("old\n", encoding="utf-8")

    assert default_lists_output_path("page.html", "csv").name == "page-lists-2.csv"
