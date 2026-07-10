from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError

from scrape_smith.tools import downloads


class FakeResponse(BytesIO):
    def __init__(self, body: bytes, headers: dict[str, str] | None = None) -> None:
        super().__init__(body)
        self.headers = headers or {}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def test_download_files_saves_target_files_and_skips_other_urls(tmp_path, monkeypatch) -> None:
    url_list = tmp_path / "urls.txt"
    url_list.write_text(
        "\n".join(
            [
                "# source list",
                "https://example.com/report.pdf",
                "https://example.com/page.html",
                "https://example.com/export",
            ]
        ),
        encoding="utf-8",
    )

    def fake_urlopen(request, timeout):  # noqa: ANN001
        url = request.full_url
        if url.endswith("report.pdf"):
            return FakeResponse(b"%PDF")
        if url.endswith("page.html"):
            return FakeResponse(b"<html></html>")
        return FakeResponse(
            b"docx",
            {"Content-Disposition": 'attachment; filename="source.docx"'},
        )

    monkeypatch.setattr(downloads, "urlopen", fake_urlopen)

    summary = downloads.download_files(url_list, tmp_path / "out", delay_seconds=0)

    assert summary.downloaded_count == 2
    assert summary.skipped_count == 1
    assert summary.failed_count == 0
    assert (tmp_path / "out" / "report.pdf").read_bytes() == b"%PDF"
    assert (tmp_path / "out" / "source.docx").read_bytes() == b"docx"


def test_download_files_sends_dummy_chrome_agent(tmp_path, monkeypatch) -> None:
    url_list = tmp_path / "urls.txt"
    url_list.write_text("https://example.com/report.pdf\n", encoding="utf-8")
    seen_headers = {}

    def fake_urlopen(request, timeout):  # noqa: ANN001
        seen_headers.update(request.header_items())
        return FakeResponse(b"%PDF")

    monkeypatch.setattr(downloads, "urlopen", fake_urlopen)

    downloads.download_files(url_list, tmp_path / "out", delay_seconds=0)

    user_agent = seen_headers["User-agent"]
    assert "Chrome/" in user_agent
    assert "scrape-smith/" not in user_agent
    assert seen_headers["Accept"] == "*/*"
    assert seen_headers["Accept-language"] == "en-US,en;q=0.9"


def test_download_files_uses_content_type_and_epoch_fallback(tmp_path, monkeypatch) -> None:
    url_list = tmp_path / "urls.txt"
    url_list.write_text("https://example.com/download\n", encoding="utf-8")

    def fake_urlopen(request, timeout):  # noqa: ANN001
        return FakeResponse(b"csv", {"Content-Type": "text/csv; charset=utf-8"})

    monkeypatch.setattr(downloads, "urlopen", fake_urlopen)
    monkeypatch.setattr(downloads.time, "time", lambda: 1_700_000_000.123)

    summary = downloads.download_files(url_list, tmp_path / "out", delay_seconds=0)

    assert summary.downloaded_count == 1
    output_path = summary.results[0].path
    assert output_path == tmp_path / "out" / "1700000000123.csv"
    assert output_path.read_bytes() == b"csv"


def test_download_files_accepts_pptx_urls(tmp_path, monkeypatch) -> None:
    url_list = tmp_path / "urls.txt"
    url_list.write_text("https://example.com/slides.pptx\n", encoding="utf-8")

    def fake_urlopen(request, timeout):  # noqa: ANN001
        return FakeResponse(b"pptx")

    monkeypatch.setattr(downloads, "urlopen", fake_urlopen)

    summary = downloads.download_files(url_list, tmp_path / "out", delay_seconds=0)

    assert summary.downloaded_count == 1
    assert (tmp_path / "out" / "slides.pptx").read_bytes() == b"pptx"


def test_download_files_avoids_overwriting_existing_files(tmp_path, monkeypatch) -> None:
    url_list = tmp_path / "urls.txt"
    url_list.write_text("https://example.com/report.pdf\n", encoding="utf-8")
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    (output_dir / "report.pdf").write_bytes(b"old")

    def fake_urlopen(request, timeout):  # noqa: ANN001
        return FakeResponse(b"new")

    monkeypatch.setattr(downloads, "urlopen", fake_urlopen)

    summary = downloads.download_files(url_list, output_dir, delay_seconds=0)

    assert summary.results[0].path == output_dir / "report-2.pdf"
    assert (output_dir / "report.pdf").read_bytes() == b"old"
    assert (output_dir / "report-2.pdf").read_bytes() == b"new"


def test_download_files_records_failures_and_keeps_going(tmp_path, monkeypatch) -> None:
    url_list = tmp_path / "urls.txt"
    url_list.write_text(
        "https://example.com/missing.pdf\nhttps://example.com/report.csv\n",
        encoding="utf-8",
    )

    def fake_urlopen(request, timeout):  # noqa: ANN001
        if request.full_url.endswith("missing.pdf"):
            raise HTTPError(request.full_url, 404, "Not Found", {}, None)
        return FakeResponse(b"name,value\n")

    monkeypatch.setattr(downloads, "urlopen", fake_urlopen)

    summary = downloads.download_files(url_list, tmp_path / "out", delay_seconds=0)

    assert summary.failed_count == 1
    assert summary.downloaded_count == 1
    assert (tmp_path / "out" / "report.csv").read_text(encoding="utf-8") == "name,value\n"


def test_default_download_dir_avoids_existing_directories(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("urls-downloads").mkdir()
    Path("urls-downloads-2").mkdir()

    assert downloads.default_download_dir("urls.txt") == Path("urls-downloads-3")
