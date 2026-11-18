#!/usr/bin/env python3
"""Measure download throughput by fetching the same URL ten times."""

import argparse
import sys
import time
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024
MB = 1_000_000


def positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a positive number") from exc
    if not 0 < number < float("inf"):
        raise argparse.ArgumentTypeError("timeout must be a positive finite number")
    return number


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download a URL 10 times sequentially and measure average speed."
    )
    parser.add_argument("url", help="HTTP or HTTPS URL of a downloadable resource")
    parser.add_argument(
        "--timeout",
        type=positive_float,
        default=60.0,
        metavar="SECONDS",
        help="socket timeout per request (default: 60 seconds)",
    )
    args = parser.parse_args()

    try:
        parsed_url = urlsplit(args.url)
        if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:
            raise ValueError
    except ValueError:
        parser.error("url must be an absolute HTTP or HTTPS URL")

    total_bytes = 0
    total_seconds = 0.0

    for request_number in range(1, REQUEST_COUNT + 1):
        request = Request(
            args.url,
            headers={
                "Accept-Encoding": "identity",
                "Cache-Control": "no-cache",
                "User-Agent": "python-download-speed-check/1.0",
            },
        )
        started = time.perf_counter()
        try:
            with urlopen(request, timeout=args.timeout) as response:
                while chunk := response.read(CHUNK_SIZE):
                    total_bytes += len(chunk)
        except (OSError, URLError) as exc:
            print(f"Request {request_number}/{REQUEST_COUNT} failed: {exc}", file=sys.stderr)
            return 1
        total_seconds += time.perf_counter() - started

    print(f"Requests: {REQUEST_COUNT}")
    print(f"Average request time: {total_seconds / REQUEST_COUNT:.3f} s")
    bytes_per_second = total_bytes / total_seconds
    print(f"Downloaded: {total_bytes} bytes ({total_bytes / MB:.3f} MB)")
    print(f"Download speed: {bytes_per_second:.0f} B/s ({bytes_per_second / MB:.3f} MB/s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
