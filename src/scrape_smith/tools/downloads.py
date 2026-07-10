"""Download file URLs into a local directory."""

from __future__ import annotations

import shutil
import time
from collections.abc import Callable
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import unquote
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen

TARGET_EXTENSIONS = frozenset({".csv", ".pdf", ".docx", ".xlsx", ".pptx"})
CONTENT_TYPE_EXTENSIONS = {
    "application/csv": ".csv",
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/csv": ".csv",
}
DEFAULT_DELAY_SECONDS = 1.0
DEFAULT_TIMEOUT_SECONDS = 30
SAFETY_WARNING = (
    "Warning: Treat downloaded files as untrusted. "
    "Scan them before opening, and do not open files blindly."
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

Reporter = Callable[[str], None]


@dataclass(frozen=True)
class DownloadResult:
    """Result for one URL from a download run."""

    url: str
    status: str
    path: Path | None = None
    reason: str | None = None


@dataclass(frozen=True)
class DownloadSummary:
    """Summary for a file download run."""

    output_dir: Path
    results: list[DownloadResult]

    @property
    def downloaded_count(self) -> int:
        return sum(1 for result in self.results if result.status == "downloaded")

    @property
    def skipped_count(self) -> int:
        return sum(1 for result in self.results if result.status == "skipped")

    @property
    def failed_count(self) -> int:
        return sum(1 for result in self.results if result.status == "failed")


def download_files(
    url_list_path: str | Path,
    output_dir: str | Path | None = None,
    *,
    delay_seconds: float = DEFAULT_DELAY_SECONDS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    reporter: Reporter | None = None,
) -> DownloadSummary:
    """Download target file URLs listed in a text file.

    Blank lines and lines starting with ``#`` are ignored. Downloads run
    sequentially with a delay between requests by default.
    """

    source_path = Path(url_list_path)
    urls = read_url_list(source_path)
    destination = Path(output_dir) if output_dir else default_download_dir(source_path)
    destination.mkdir(parents=True, exist_ok=True)

    _report(reporter, f"Start download run: {len(urls)} URL(s)")
    _report(reporter, f"Output directory: {destination}")
    _report(reporter, SAFETY_WARNING)

    results: list[DownloadResult] = []
    for index, url in enumerate(urls, start=1):
        if index > 1 and delay_seconds > 0:
            time.sleep(delay_seconds)
        result = download_url(url, destination, timeout_seconds=timeout_seconds)
        results.append(result)
        _report_result(reporter, result)

    summary = DownloadSummary(output_dir=destination, results=results)
    _report(
        reporter,
        (
            "End download run: "
            f"{summary.downloaded_count} downloaded, "
            f"{summary.skipped_count} skipped, "
            f"{summary.failed_count} failed"
        ),
    )
    return summary


def read_url_list(url_list_path: str | Path) -> list[str]:
    """Read non-empty, non-comment URL lines from a text file."""

    urls: list[str] = []
    for line in Path(url_list_path).read_text(encoding="utf-8").splitlines():
        candidate = line.strip()
        if candidate and not candidate.startswith("#"):
            urls.append(candidate)
    return urls


def download_url(
    url: str,
    output_dir: str | Path,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> DownloadResult:
    """Download one URL when it resolves to a supported target file."""

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return DownloadResult(url=url, status="skipped", reason="unsupported URL scheme")

    request = Request(url, headers=REQUEST_HEADERS)
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            filename = response_filename(response.headers.get("Content-Disposition"))
            filename = filename or url_filename(url)
            extension = target_extension(filename)
            if extension is None:
                extension = content_type_extension(response.headers.get("Content-Type"))
                if extension:
                    filename = None
            if extension is None:
                return DownloadResult(url=url, status="skipped", reason="not a target file")

            safe_name = safe_filename(filename) if filename else fallback_filename(extension)
            output_path = available_path(Path(output_dir) / safe_name)
            with output_path.open("wb") as output_file:
                shutil.copyfileobj(response, output_file)
            return DownloadResult(url=url, status="downloaded", path=output_path)
    except HTTPError as error:
        return DownloadResult(url=url, status="failed", reason=f"HTTP {error.code}")
    except OSError as error:
        return DownloadResult(url=url, status="failed", reason=str(error))


def default_download_dir(url_list_path: str | Path) -> Path:
    """Return a collision-safe output directory for a URL list file."""

    source_path = Path(url_list_path)
    stem = source_path.stem or "urls"
    return available_directory(Path(f"{stem}-downloads"))


def available_directory(path: Path) -> Path:
    """Return ``path`` or a suffixed sibling that does not exist."""

    if not path.exists():
        return path

    counter = 2
    while True:
        candidate = path.with_name(f"{path.name}-{counter}")
        if not candidate.exists():
            return candidate
        counter += 1


def available_path(path: Path) -> Path:
    """Return ``path`` or a suffixed sibling that does not exist."""

    if not path.exists():
        return path

    counter = 2
    while True:
        candidate = path.with_stem(f"{path.stem}-{counter}")
        if not candidate.exists():
            return candidate
        counter += 1


def response_filename(content_disposition: str | None) -> str | None:
    """Extract a filename from a Content-Disposition header."""

    if not content_disposition:
        return None

    message = Message()
    message["Content-Disposition"] = content_disposition
    filename = message.get_filename()
    return Path(filename).name if filename else None


def url_filename(url: str) -> str | None:
    """Extract a filename from a URL path."""

    name = Path(unquote(urlparse(url).path)).name
    return name or None


def target_extension(filename: str | None) -> str | None:
    """Return a supported target extension for a filename."""

    if not filename:
        return None
    suffix = Path(filename).suffix.lower()
    return suffix if suffix in TARGET_EXTENSIONS else None


def content_type_extension(content_type: str | None) -> str | None:
    """Return a supported target extension for a Content-Type value."""

    if not content_type:
        return None
    media_type = content_type.split(";", 1)[0].strip().lower()
    return CONTENT_TYPE_EXTENSIONS.get(media_type)


def safe_filename(filename: str) -> str:
    """Return a filesystem-safe basename preserving the original extension."""

    name = Path(filename).name.strip()
    safe = "".join(
        character if character not in {"/", "\\", "\0"} else "-" for character in name
    )
    return safe.strip(". ") or fallback_filename(".dat")


def fallback_filename(extension: str) -> str:
    """Return an epoch-based fallback filename with fixed-width milliseconds."""

    return f"{int(time.time() * 1000):013d}{extension}"


def _report(reporter: Reporter | None, message: str) -> None:
    if reporter:
        reporter(message)


def _report_result(reporter: Reporter | None, result: DownloadResult) -> None:
    if result.status == "downloaded" and result.path:
        _report(reporter, f"Downloaded {result.url} -> {result.path}")
    elif result.status == "skipped":
        _report(reporter, f"Skipped {result.url}: {result.reason}")
    elif result.status == "failed":
        _report(reporter, f"Failed {result.url}: {result.reason}")
