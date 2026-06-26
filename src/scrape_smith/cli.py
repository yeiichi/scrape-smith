"""Command line interface for scrape-smith."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import urlparse

from scrape_smith.tools.tables import HtmlTable
from scrape_smith.tools.tables import extract_tables

SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scrape")
    subparsers = parser.add_subparsers(dest="command", required=True)

    table_parser = subparsers.add_parser("tables", help="Extract tables from HTML.")
    table_parser.add_argument("target", help="HTML file path or HTTP(S) URL.")
    table_parser.add_argument(
        "--format",
        choices=("json", "csv"),
        default="csv",
        help="Output file format. Defaults to csv.",
    )
    table_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path. Defaults to a safe source-based filename.",
    )
    table_parser.add_argument(
        "--index",
        type=int,
        help="Output one table by zero-based index.",
    )
    table_parser.set_defaults(func=run_table)

    return parser


def run_table(args: argparse.Namespace) -> int:
    tables = extract_tables(args.target)

    if args.index is not None:
        try:
            tables = [tables[args.index]]
        except IndexError:
            print(f"table index out of range: {args.index}", file=sys.stderr)
            return 2

    output_path = args.output or default_output_path(args.target, args.format)

    if args.format == "json":
        write_json(tables, output_path)
        return 0

    write_csv(tables, output_path)
    return 0


def write_json(tables: list[HtmlTable], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump([table.to_dict() for table in tables], output_file, ensure_ascii=False, indent=2)
        output_file.write("\n")


def write_csv(tables: list[HtmlTable], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file)
        for table_index, table in enumerate(tables):
            if table_index:
                writer.writerow([])
            if table.headers:
                writer.writerow(table.headers)
            writer.writerows(table.rows)


def default_output_path(target: str, output_format: str) -> Path:
    return available_output_path(f"{source_slug(target)}-tables", output_format)


def available_output_path(stem: str, suffix: str) -> Path:
    output_path = Path(f"{stem}.{suffix}")
    if not output_path.exists():
        return output_path

    counter = 2
    while True:
        candidate = Path(f"{stem}-{counter}.{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def source_slug(target: str) -> str:
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https"}:
        source_name = Path(parsed.path).name or parsed.netloc
    else:
        source_name = Path(target).stem or Path(target).name

    slug = SAFE_NAME_PATTERN.sub("-", source_name).strip(".-_").lower()
    return slug or "tables"


if __name__ == "__main__":
    raise SystemExit(main())
