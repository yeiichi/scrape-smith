"""Extract list data from HTML documents."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from scrape_smith.tools.tables import read_html

LIST_TAGS = frozenset({"ul", "ol", "dl"})


@dataclass(frozen=True)
class HtmlList:
    """An ordered or unordered list extracted from an HTML document."""

    tag: str  # "ul" or "ol"
    items: list[str]

    def to_dict(self) -> dict[str, object]:
        return {"tag": self.tag, "items": self.items}


@dataclass(frozen=True)
class HtmlDefinitionList:
    """A definition list extracted from an HTML document."""

    items: list[dict[str, str]]  # [{"term": ..., "description": ...}]

    def to_dict(self) -> dict[str, object]:
        return {"tag": "dl", "items": self.items}


def extract_lists(target: str | Path) -> list[HtmlList | HtmlDefinitionList]:
    """Extract lists from a local HTML file path or HTTP(S) URL."""

    html = read_html(target)
    return extract_lists_from_html(html)


def extract_lists_from_html(html: str) -> list[HtmlList | HtmlDefinitionList]:
    """Extract lists from an HTML string."""

    parser = _ListParser()
    parser.feed(html)
    parser.close()
    return parser.results


class _ListParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.results: list[HtmlList | HtmlDefinitionList] = []
        self._list_depth = 0
        self._root_tag: str | None = None
        self._items: list[str] = []
        self._dl_items: list[dict[str, str]] = []
        self._pending_dt: str | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in LIST_TAGS:
            self._list_depth += 1
            if self._list_depth == 1:
                self._root_tag = tag
                self._items = []
                self._dl_items = []
                self._pending_dt = None
                self._cell = None
            return

        if self._list_depth != 1:
            return

        if tag == "li" and self._root_tag in {"ul", "ol"}:
            self._cell = []
        elif tag in {"dt", "dd"} and self._root_tag == "dl":
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in LIST_TAGS:
            if self._list_depth == 1:
                if self._root_tag in {"ul", "ol"}:
                    self.results.append(HtmlList(tag=self._root_tag, items=self._items))
                elif self._root_tag == "dl":
                    if self._pending_dt is not None:
                        self._dl_items.append({"term": self._pending_dt, "description": ""})
                    self.results.append(HtmlDefinitionList(items=self._dl_items))
                self._root_tag = None
                self._cell = None
            self._list_depth = max(0, self._list_depth - 1)
            return

        if self._list_depth != 1 or self._cell is None or tag not in {"li", "dt", "dd"}:
            return

        text = _clean_text("".join(self._cell))
        self._cell = None

        if tag == "li":
            if text:
                self._items.append(text)
        elif tag == "dt":
            self._pending_dt = text
        elif tag == "dd":
            term = self._pending_dt or ""
            self._dl_items.append({"term": term, "description": text})
            self._pending_dt = None

    def handle_data(self, data: str) -> None:
        if self._list_depth == 1 and self._cell is not None:
            self._cell.append(data)


def _clean_text(text: str) -> str:
    return " ".join(text.split())
