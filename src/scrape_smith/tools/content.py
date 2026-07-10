"""Extract body content from HTML documents as JSONL-ready records."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import TextIO

from scrape_smith.tools.tables import read_html

CONTENT_TAGS = frozenset({
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "a",
    "li", "td", "th", "blockquote", "figcaption",
    "dt", "dd", "caption", "label", "button",
})
IGNORED_TAGS = frozenset({"script", "style", "template", "noscript"})


@dataclass
class _Capture:
    tag: str
    attrs: dict[str, str]
    parts: list[str]
    sequence: int


def extract_content_records(target: str | Path) -> list[dict[str, str]]:
    """Extract body text records from a local HTML file path or HTTP(S) URL."""

    html = read_html(target)
    return extract_content_records_from_html(html)


def extract_content_records_from_html(html: str) -> list[dict[str, str]]:
    """Extract JSONL-ready body text records from an HTML string."""

    parser = _ContentParser()
    parser.feed(html)
    parser.close()
    return parser.records


def write_jsonl(records: list[dict[str, str]], output_file: TextIO) -> None:
    """Write content records as newline-delimited JSON."""

    for record in records:
        json.dump(record, output_file, ensure_ascii=False)
        output_file.write("\n")


class _ContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.records: list[dict[str, str]] = []
        self._body_depth = 0
        self._ignored_depth = 0
        self._captures: list[_Capture] = []
        self._next_sequence = 0
        self._finished: list[tuple[int, dict[str, str]]] = []

    def close(self) -> None:
        super().close()
        self._finish_open_captures()
        self.records = [record for _, record in sorted(self._finished, key=lambda item: item[0])]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "body":
            self._body_depth += 1
            return

        if not self._in_body:
            return

        if tag in IGNORED_TAGS:
            self._ignored_depth += 1
            return

        if self._ignored_depth:
            return

        if tag in CONTENT_TAGS:
            self._captures.append(
                _Capture(
                    tag=tag,
                    attrs={name.lower(): value or "" for name, value in attrs},
                    parts=[],
                    sequence=self._next_sequence,
                )
            )
            self._next_sequence += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "body":
            self._finish_open_captures()
            self._body_depth = max(0, self._body_depth - 1)
            return

        if not self._in_body:
            return

        if tag in IGNORED_TAGS and self._ignored_depth:
            self._ignored_depth -= 1
            return

        if self._ignored_depth or tag not in CONTENT_TAGS:
            return

        for index in range(len(self._captures) - 1, -1, -1):
            capture = self._captures[index]
            if capture.tag == tag:
                del self._captures[index]
                self._finish_capture(capture)
                return

    def handle_data(self, data: str) -> None:
        if not self._in_body or self._ignored_depth:
            return

        for capture in self._captures:
            capture.parts.append(data)

    @property
    def _in_body(self) -> bool:
        return self._body_depth > 0

    def _finish_capture(self, capture: _Capture) -> None:
        text = _clean_text("".join(capture.parts))
        if not text:
            return

        record = {capture.tag: text}
        if capture.tag == "a" and capture.attrs.get("href"):
            record["href"] = capture.attrs["href"]
        self._finished.append((capture.sequence, record))

    def _finish_open_captures(self) -> None:
        captures = self._captures
        self._captures = []
        for capture in captures:
            self._finish_capture(capture)


def _clean_text(text: str) -> str:
    normalized = " ".join(text.split())
    return re.sub(r"\s+([,.;:!?])", r"\1", normalized)
