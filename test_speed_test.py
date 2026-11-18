"""Check complete, sequential downloads without external network access."""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch
from urllib.error import HTTPError

import speed_test


BODY = b"download-test" * 1000


class FakeResponse:
    def __init__(self, owner):
        self.owner = owner
        self.body = io.BytesIO(BODY)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        if self.body.read():
            raise AssertionError("Response was not fully read")
        self.owner.active = False

    def read(self, size):
        return self.body.read(size)


class FakeServer:
    def __init__(self):
        self.requests = 0
        self.active = False

    def open(self, request, timeout):
        if self.active:
            raise AssertionError("A new request started before the last one finished")
        self.active = True
        self.requests += 1
        return FakeResponse(self)


class SpeedTestTests(unittest.TestCase):
    def test_reads_ten_responses_sequentially(self):
        server = FakeServer()
        output = io.StringIO()
        clock = [tick for second in range(10) for tick in (second, second + 1)]

        with (
            patch("sys.argv", ["speed_test.py", "https://example.com/file"]),
            patch.object(speed_test, "urlopen", side_effect=server.open),
            patch.object(speed_test.time, "perf_counter", side_effect=clock),
            redirect_stdout(output),
        ):
            exit_code = speed_test.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(server.requests, 10)
        self.assertFalse(server.active)
        self.assertIn("Requests: 10", output.getvalue())
        self.assertIn("Average request time: 1.000 s", output.getvalue())
        self.assertIn(f"Downloaded: {10 * len(BODY)} bytes", output.getvalue())
        self.assertIn(f"Download speed: {len(BODY) / 1048576:.3f} MiB/s", output.getvalue())

    def test_stops_on_http_error(self):
        error = HTTPError("https://example.com/file", 500, "Server Error", {}, None)
        output = io.StringIO()
        with (
            patch("sys.argv", ["speed_test.py", "https://example.com/file"]),
            patch.object(speed_test, "urlopen", side_effect=error) as open_mock,
            redirect_stderr(output),
        ):
            exit_code = speed_test.main()

        self.assertEqual(exit_code, 1)
        open_mock.assert_called_once()
        self.assertIn("Request 1/10 failed", output.getvalue())


if __name__ == "__main__":
    unittest.main()
