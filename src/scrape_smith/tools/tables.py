"""Extract tabular data from HTML documents."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class HtmlTable:
    """A table extracted from an HTML document."""

    caption: str | None
    headers: list[str]
    rows: list[list[str]]

    def to_dict(self) -> dict[str, object]:
        return {
            "caption": self.caption,
            "headers": self.headers,
            "rows": self.rows,
        }


def extract_tables(target: str | Path) -> list[HtmlTable]:
    """Extract tables from a local HTML file path or HTTP(S) URL."""

    html = read_html(target)
    return extract_tables_from_html(html)


def extract_tables_from_html(html: str) -> list[HtmlTable]:
    """Extract tables from an HTML string."""

    parser = _TableParser()
    parser.feed(html)
    parser.close()
    return parser.tables


def read_html(target: str | Path) -> str:
    """Read HTML from a local path or HTTP(S) URL."""

    target_text = str(target)
    parsed = urlparse(target_text)
    if parsed.scheme in {"http", "https"}:
        request = Request(target_text, headers={"User-Agent": "scrape-smith/0.1"})
        with urlopen(request, timeout=30) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")

    return Path(target).read_text(encoding="utf-8")


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[HtmlTable] = []
        self._table_depth = 0
        self._caption: str | None = None
        self._headers: list[str] = []
        self._rows: list[list[str]] = []
        self._current_row: list[str] | None = None
        self._current_row_header_flags: list[bool] = []
        self._current_cell_parts: list[str] | None = None
        self._current_cell_is_header = False
        self._caption_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._caption = None
                self._headers = []
                self._rows = []
            return

        if self._table_depth != 1:
            return

        if tag == "caption":
            self._caption_parts = []
        elif tag == "tr":
            self._current_row = []
            self._current_row_header_flags = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell_parts = []
            self._current_cell_is_header = tag == "th"

    def handle_endtag(self, tag: str) -> None:
        if tag == "table":
            if self._table_depth == 1:
                self.tables.append(
                    HtmlTable(caption=self._caption, headers=self._headers, rows=self._rows)
                )
            self._table_depth = max(0, self._table_depth - 1)
            return

        if self._table_depth != 1:
            return

        if tag == "caption" and self._caption_parts is not None:
            self._caption = _clean_text("".join(self._caption_parts)) or None
            self._caption_parts = None
        elif tag in {"td", "th"} and self._current_cell_parts is not None:
            cell = _clean_text("".join(self._current_cell_parts))
            if self._current_row is not None:
                self._current_row.append(cell)
                self._current_row_header_flags.append(self._current_cell_is_header)
            self._current_cell_parts = None
            self._current_cell_is_header = False
        elif tag == "tr" and self._current_row is not None:
            if self._is_column_header_row():
                self._headers = self._current_row
            else:
                self._rows.append(self._current_row)
            self._current_row = None
            self._current_row_header_flags = []

    def handle_data(self, data: str) -> None:
        if self._table_depth != 1:
            return

        if self._caption_parts is not None:
            self._caption_parts.append(data)
        elif self._current_cell_parts is not None:
            self._current_cell_parts.append(data)

    def _is_column_header_row(self) -> bool:
        return (
            bool(self._current_row)
            and not self._headers
            and not self._rows
            and all(self._current_row_header_flags)
        )


def _clean_text(text: str) -> str:
    return " ".join(text.split())
