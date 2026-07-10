"""Command line interface for scrape-smith."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO
from urllib.parse import urlparse

from scrape_smith.tools.content import extract_content_records
from scrape_smith.tools.content import write_jsonl
from scrape_smith.tools.downloads import DEFAULT_DELAY_SECONDS
from scrape_smith.tools.downloads import download_files
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
    table_parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress success reports on stdout.",
    )
    table_parser.set_defaults(func=run_table)

    download_parser = subparsers.add_parser(
        "download",
        help="Download target files from a URL list.",
    )
    download_parser.add_argument(
        "url_list",
        type=Path,
        help="Text file containing one URL per line.",
    )
    download_parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory. Defaults to a safe name based on the URL list file.",
    )
    download_parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help=f"Seconds to wait between requests. Defaults to {DEFAULT_DELAY_SECONDS:g}.",
    )
    download_parser.set_defaults(func=run_download)

    content_parser = subparsers.add_parser(
        "content",
        help="Convert HTML body content to JSONL.",
    )
    content_parser.add_argument("target", help="HTML file path or HTTP(S) URL.")
    content_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output JSONL file path. Defaults to a safe source-based filename.",
    )
    content_parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress success reports on stdout.",
    )
    content_parser.set_defaults(func=run_content)

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

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        write_tables(tables, args.format, output_file)
    if not args.quiet:
        print(f"Wrote {len(tables)} {pluralize('table', len(tables))} to {output_path}")
    return 0


def run_download(args: argparse.Namespace) -> int:
    summary = download_files(
        args.url_list,
        args.output_dir,
        delay_seconds=args.delay,
        reporter=print,
    )
    return 1 if summary.failed_count else 0


def run_content(args: argparse.Namespace) -> int:
    records = extract_content_records(args.target)
    output_path = args.output or default_content_output_path(args.target)

    with output_path.open("w", encoding="utf-8") as output_file:
        write_jsonl(records, output_file)
    if not args.quiet:
        print(f"Wrote {len(records)} {pluralize('record', len(records))} to {output_path}")
    return 0


def write_tables(tables: list[HtmlTable], output_format: str, output_file: TextIO) -> None:
    if output_format == "json":
        write_json(tables, output_file)
    else:
        write_csv(tables, output_file)


def write_json(tables: list[HtmlTable], output_file: TextIO) -> None:
    json.dump([table.to_dict() for table in tables], output_file, ensure_ascii=False, indent=2)
    output_file.write("\n")


def write_csv(tables: list[HtmlTable], output_file: TextIO) -> None:
    writer = csv.writer(output_file)
    for table_index, table in enumerate(tables):
        if table_index:
            writer.writerow([])
        if table.headers:
            writer.writerow(table.headers)
        writer.writerows(table.rows)


def pluralize(word: str, count: int) -> str:
    if count == 1:
        return word
    return f"{word}s"


def default_output_path(target: str, output_format: str) -> Path:
    return available_output_path(f"{source_slug(target)}-tables", output_format)


def default_content_output_path(target: str) -> Path:
    return available_output_path(f"{source_slug(target)}-content", "jsonl")


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
