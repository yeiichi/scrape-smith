import csv
import json
from io import BytesIO

from scrape_smith.tools import downloads
from scrape_smith.cli import default_content_output_path
from scrape_smith.cli import default_output_path
from scrape_smith.cli import main
from scrape_smith.cli import source_slug


class FakeResponse(BytesIO):
    def __init__(self, body: bytes, headers: dict[str, str] | None = None) -> None:
        super().__init__(body)
        self.headers = headers or {}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


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
    assert captured.out == "Wrote 1 table to page-tables.csv\n"
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
    assert captured.out == f"Wrote 1 table to {output_path}\n"
    assert captured.err == ""
    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        {"caption": "People", "headers": ["Name"], "rows": [["Ada"]]}
    ]


def test_tables_command_quiet_suppresses_success_report(tmp_path, capsys) -> None:
    html_path = tmp_path / "page.html"
    output_path = tmp_path / "tables.csv"
    html_path.write_text(
        """
        <table>
          <tr><th>Name</th></tr>
          <tr><td>Ada</td></tr>
        </table>
        """,
        encoding="utf-8",
    )

    exit_code = main(["tables", str(html_path), "-o", str(output_path), "--quiet"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""
    with output_path.open(encoding="utf-8", newline="") as output_file:
        assert list(csv.reader(output_file)) == [["Name"], ["Ada"]]


def test_tables_command_writes_json_to_default_file(tmp_path, monkeypatch, capsys) -> None:
    html_path = tmp_path / "page.html"
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
    monkeypatch.chdir(tmp_path)

    exit_code = main(["tables", str(html_path), "--format", "json"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "Wrote 1 table to page-tables.json\n"
    assert captured.err == ""
    assert json.loads((tmp_path / "page-tables.json").read_text(encoding="utf-8")) == [
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
    assert captured.out == f"Wrote 2 tables to {output_path}\n"
    assert captured.err == ""
    with output_path.open(encoding="utf-8", newline="") as output_file:
        assert list(csv.reader(output_file)) == [["Name"], ["Ada"], [], ["Year"], ["2026"]]


def test_default_output_path_avoids_overwriting_existing_files(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "page-tables.csv").write_text("old\n", encoding="utf-8")
    (tmp_path / "page-tables-2.csv").write_text("older\n", encoding="utf-8")

    assert default_output_path("page.html", "csv").name == "page-tables-3.csv"


def test_default_content_output_path_avoids_overwriting_existing_files(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "page-content.jsonl").write_text("old\n", encoding="utf-8")
    (tmp_path / "page-content-2.jsonl").write_text("older\n", encoding="utf-8")

    assert default_content_output_path("page.html").name == "page-content-3.jsonl"


def test_source_slug_uses_safe_source_names() -> None:
    assert source_slug("https://yeiichi.github.io/claim-class-model") == "claim-class-model"
    assert source_slug("https://example.com/") == "example.com"
    assert source_slug("My Weird: Report?.html") == "my-weird-report"


def test_download_command_reports_important_events(tmp_path, monkeypatch, capsys) -> None:
    url_list = tmp_path / "urls.txt"
    url_list.write_text("https://example.com/report.pdf\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    def fake_urlopen(request, timeout):  # noqa: ANN001
        return FakeResponse(b"%PDF")

    monkeypatch.setattr(downloads, "urlopen", fake_urlopen)

    exit_code = main(["download", str(url_list), "--delay", "0"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert captured.out == (
        "Start download run: 1 URL(s)\n"
        "Output directory: urls-downloads\n"
        "Warning: Treat downloaded files as untrusted. "
        "Scan them before opening, and do not open files blindly.\n"
        "Downloaded https://example.com/report.pdf -> urls-downloads/report.pdf\n"
        "End download run: 1 downloaded, 0 skipped, 0 failed\n"
    )
    assert (tmp_path / "urls-downloads" / "report.pdf").read_bytes() == b"%PDF"


def test_content_command_writes_jsonl_by_default(tmp_path, monkeypatch, capsys) -> None:
    html_path = tmp_path / "page.html"
    html_path.write_text(
        """
        <html>
          <body>
            <h1>Title</h1>
            <p>Hello <a href="/docs">docs</a>.</p>
          </body>
        </html>
        """,
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    exit_code = main(["content", str(html_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert captured.out == "Wrote 3 records to page-content.jsonl\n"
    lines = (tmp_path / "page-content.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line) for line in lines] == [
        {"h1": "Title"},
        {"p": "Hello docs."},
        {"a": "docs", "href": "/docs"},
    ]
