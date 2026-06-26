import csv
import json

from scrape_smith.cli import default_output_path
from scrape_smith.cli import main
from scrape_smith.cli import source_slug


def test_tables_command_writes_csv_by_default(tmp_path, monkeypatch, capsys) -> None:
    html_path = tmp_path / "page.html"
    html_path.write_text(
        """
        <table>
          <tr><th>Name</th><th>Role</th></tr>
          <tr><td>Ada</td><td>Engineer</td></tr>
        </table>
        """,
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    exit_code = main(["tables", str(html_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""
    with (tmp_path / "page-tables.csv").open(encoding="utf-8", newline="") as output_file:
        assert list(csv.reader(output_file)) == [["Name", "Role"], ["Ada", "Engineer"]]


def test_tables_command_writes_json_file(tmp_path, capsys) -> None:
    html_path = tmp_path / "page.html"
    output_path = tmp_path / "tables.json"
    html_path.write_text(
        """
        <table>
          <caption>People</caption>
          <tr><th>Name</th></tr>
          <tr><td>Ada</td></tr>
        </table>
        """,
        encoding="utf-8",
    )

    exit_code = main(["tables", str(html_path), "--format", "json", "-o", str(output_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""
    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {"caption": "People", "headers": ["Name"], "rows": [["Ada"]]}
    ]


def test_tables_command_writes_multiple_tables_to_one_csv_file(tmp_path, capsys) -> None:
    html_path = tmp_path / "page.html"
    output_path = tmp_path / "tables.csv"
    html_path.write_text(
        """
        <table>
          <tr><th>Name</th></tr>
          <tr><td>Ada</td></tr>
        </table>
        <table>
          <tr><th>Year</th></tr>
          <tr><td>2026</td></tr>
        </table>
        """,
        encoding="utf-8",
    )

    exit_code = main(["tables", str(html_path), "-o", str(output_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""
    with output_path.open(encoding="utf-8", newline="") as output_file:
        assert list(csv.reader(output_file)) == [["Name"], ["Ada"], [], ["Year"], ["2026"]]


def test_default_output_path_avoids_overwriting_existing_files(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "page-tables.csv").write_text("old\n", encoding="utf-8")
    (tmp_path / "page-tables-2.csv").write_text("older\n", encoding="utf-8")

    assert default_output_path("page.html", "csv").name == "page-tables-3.csv"


def test_source_slug_uses_safe_source_names() -> None:
    assert source_slug("https://yeiichi.github.io/claim-class-model") == "claim-class-model"
    assert source_slug("https://example.com/") == "example.com"
    assert source_slug("My Weird: Report?.html") == "my-weird-report"
