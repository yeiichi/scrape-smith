"""Extract all content, tables, and lists from an HTML document as JSONL records."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import TextIO

from scrape_smith.tools.tables import read_html

_CONTENT_TAGS = frozenset({
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "a", "blockquote", "figcaption", "label", "button",
})
_IGNORED_TAGS = frozenset({"script", "style", "template", "noscript"})
_LIST_TAGS = frozenset({"ul", "ol", "dl"})


@dataclass
class _ContentCapture:
    tag: str
    attrs: dict[str, str]
    parts: list[str]
    sequence: int


def extract_all(target: str | Path) -> list[dict[str, str]]:
    """Extract all records from a local HTML file path or HTTP(S) URL."""

    html = read_html(target)
    return extract_all_from_html(html)


def extract_all_from_html(html: str) -> list[dict[str, str]]:
    """Extract all records from an HTML string.

    Returns a list of ``{"type": ..., "data": ...}`` dicts in document order.
    ``type`` is one of ``"content"``, ``"table"``, or ``"list"``.
    ``data`` is a JSON string with the record payload.
    """

    parser = _ExtractParser()
    parser.feed(html)
    parser.close()
    return parser.records


def write_jsonl(records: list[dict[str, str]], output_file: TextIO) -> None:
    """Write extract records as newline-delimited JSON."""

    for record in records:
        json.dump(record, output_file, ensure_ascii=False)
        output_file.write("\n")


class _ExtractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._next_seq = 0
        self._finished: list[tuple[int, dict[str, str]]] = []

        # Body / ignored tracking
        self._body_depth = 0
        self._ignored_depth = 0

        # Table state
        self._table_depth = 0
        self._table_start_seq: int | None = None
        self._table_caption: str | None = None
        self._table_caption_parts: list[str] | None = None
        self._table_headers: list[str] = []
        self._table_rows: list[list[str]] = []
        self._table_current_row: list[str] | None = None
        self._table_row_header_flags: list[bool] = []
        self._table_cell_parts: list[str] | None = None
        self._table_cell_is_header: bool = False

        # List state
        self._list_depth = 0
        self._list_start_seq: int | None = None
        self._list_root_tag: str | None = None
        self._list_items: list[str] = []
        self._list_dl_items: list[dict[str, str]] = []
        self._list_pending_dt: str | None = None
        self._list_cell: list[str] | None = None

        # Content state (stack for nesting)
        self._content_captures: list[_ContentCapture] = []

    @property
    def records(self) -> list[dict[str, str]]:
        return [r for _, r in sorted(self._finished, key=lambda x: x[0])]

    @property
    def _in_body(self) -> bool:
        return self._body_depth > 0

    @property
    def _in_table(self) -> bool:
        return self._table_depth > 0

    @property
    def _in_list(self) -> bool:
        return self._list_depth > 0

    def _alloc_seq(self) -> int:
        seq = self._next_seq
        self._next_seq += 1
        return seq

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()

        if tag == "body":
            self._body_depth += 1
            return

        if not self._in_body:
            return

        if tag in _IGNORED_TAGS:
            self._ignored_depth += 1
            return

        if self._ignored_depth:
            return

        # --- table ---
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._table_start_seq = self._alloc_seq()
                self._table_caption = None
                self._table_caption_parts = None
                self._table_headers = []
                self._table_rows = []
                self._table_current_row = None
            return

        if self._in_table:
            if self._table_depth == 1:
                if tag == "caption":
                    self._table_caption_parts = []
                elif tag == "tr":
                    self._table_current_row = []
                    self._table_row_header_flags = []
                elif tag in {"td", "th"} and self._table_current_row is not None:
                    self._table_cell_parts = []
                    self._table_cell_is_header = tag == "th"
            return

        # --- list ---
        if tag in _LIST_TAGS:
            self._list_depth += 1
            if self._list_depth == 1:
                self._list_start_seq = self._alloc_seq()
                self._list_root_tag = tag
                self._list_items = []
                self._list_dl_items = []
                self._list_pending_dt = None
                self._list_cell = None
            return

        if self._in_list:
            if self._list_depth == 1:
                if tag == "li" and self._list_root_tag in {"ul", "ol"}:
                    self._list_cell = []
                elif tag in {"dt", "dd"} and self._list_root_tag == "dl":
                    self._list_cell = []
            return

        # --- content ---
        if tag in _CONTENT_TAGS:
            self._content_captures.append(
                _ContentCapture(
                    tag=tag,
                    attrs={k.lower(): v or "" for k, v in attrs},
                    parts=[],
                    sequence=self._alloc_seq(),
                )
            )

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag == "body":
            self._finish_open_content_captures()
            self._body_depth = max(0, self._body_depth - 1)
            return

        if not self._in_body:
            return

        if tag in _IGNORED_TAGS and self._ignored_depth:
            self._ignored_depth -= 1
            return

        if self._ignored_depth:
            return

        # --- table ---
        if tag == "table":
            if self._table_depth == 1:
                self._finish_table()
            self._table_depth = max(0, self._table_depth - 1)
            return

        if self._in_table:
            if self._table_depth == 1:
                if tag == "caption" and self._table_caption_parts is not None:
                    self._table_caption = _clean_text("".join(self._table_caption_parts)) or None
                    self._table_caption_parts = None
                elif tag in {"td", "th"} and self._table_cell_parts is not None:
                    cell = _clean_text("".join(self._table_cell_parts))
                    if self._table_current_row is not None:
                        self._table_current_row.append(cell)
                        self._table_row_header_flags.append(self._table_cell_is_header)
                    self._table_cell_parts = None
                    self._table_cell_is_header = False
                elif tag == "tr" and self._table_current_row is not None:
                    if self._is_header_row():
                        self._table_headers = self._table_current_row
                    else:
                        self._table_rows.append(self._table_current_row)
                    self._table_current_row = None
                    self._table_row_header_flags = []
            return

        # --- list ---
        if tag in _LIST_TAGS:
            if self._list_depth == 1:
                self._finish_list()
            self._list_depth = max(0, self._list_depth - 1)
            return

        if self._in_list:
            if self._list_depth == 1 and self._list_cell is not None and tag in {"li", "dt", "dd"}:
                text = _clean_text("".join(self._list_cell))
                self._list_cell = None
                if tag == "li" and text:
                    self._list_items.append(text)
                elif tag == "dt":
                    self._list_pending_dt = text
                elif tag == "dd":
                    self._list_dl_items.append({
                        "term": self._list_pending_dt or "",
                        "description": text,
                    })
                    self._list_pending_dt = None
            return

        # --- content ---
        if tag in _CONTENT_TAGS:
            for i in range(len(self._content_captures) - 1, -1, -1):
                capture = self._content_captures[i]
                if capture.tag == tag:
                    del self._content_captures[i]
                    self._finish_content_capture(capture)
                    return

    def handle_data(self, data: str) -> None:
        if not self._in_body or self._ignored_depth:
            return

        if self._in_table and self._table_depth == 1:
            if self._table_caption_parts is not None:
                self._table_caption_parts.append(data)
            elif self._table_cell_parts is not None:
                self._table_cell_parts.append(data)
            return

        if self._in_list and self._list_depth == 1 and self._list_cell is not None:
            self._list_cell.append(data)
            return

        for capture in self._content_captures:
            capture.parts.append(data)

    def close(self) -> None:
        super().close()
        self._finish_open_content_captures()

    # --- finish helpers ---

    def _finish_table(self) -> None:
        if self._table_start_seq is None:
            return
        data = {"caption": self._table_caption, "headers": self._table_headers, "rows": self._table_rows}
        self._finished.append((self._table_start_seq, {"type": "table", "data": json.dumps(data, ensure_ascii=False)}))
        self._table_start_seq = None

    def _finish_list(self) -> None:
        if self._list_start_seq is None:
            return
        if self._list_root_tag in {"ul", "ol"}:
            data: dict[str, object] = {"tag": self._list_root_tag, "items": self._list_items}
        else:
            if self._list_pending_dt is not None:
                self._list_dl_items.append({"term": self._list_pending_dt, "description": ""})
            data = {"tag": "dl", "items": self._list_dl_items}
        self._finished.append((self._list_start_seq, {"type": "list", "data": json.dumps(data, ensure_ascii=False)}))
        self._list_start_seq = None

    def _finish_content_capture(self, capture: _ContentCapture) -> None:
        text = _clean_text("".join(capture.parts))
        if not text:
            return
        payload: dict[str, str] = {"tag": capture.tag, "text": text}
        if capture.tag == "a" and capture.attrs.get("href"):
            payload["href"] = capture.attrs["href"]
        self._finished.append((capture.sequence, {"type": "content", "data": json.dumps(payload, ensure_ascii=False)}))

    def _finish_open_content_captures(self) -> None:
        captures = self._content_captures
        self._content_captures = []
        for capture in captures:
            self._finish_content_capture(capture)

    def _is_header_row(self) -> bool:
        return (
            bool(self._table_current_row)
            and not self._table_headers
            and not self._table_rows
            and all(self._table_row_header_flags)
        )


def _clean_text(text: str) -> str:
    normalized = " ".join(text.split())
    return re.sub(r"\s+([,.;:!?])", r"\1", normalized)
