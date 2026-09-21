import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import api_server


class APIStreamTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_server = api_server.bi_server
        self.server = Mock()
        api_server.bi_server = self.server
        self.client = TestClient(api_server.app)

    def tearDown(self) -> None:
        api_server.bi_server = self.original_server

    def test_stream_endpoint_returns_sse_events(self) -> None:
        events = [
            'event: chunk\ndata: {"content": "SELECT"}\n\n',
            'event: complete_sql\ndata: {"sql": "SELECT 1"}\n\n',
            'event: result\ndata: {"columns": ["value"], "rows": [[1]], "row_count": 1}\n\n',
        ]
        self.server.run_stream.return_value = iter(events)

        response = self.client.post(
            "/api/v1/query/stream",
            json={"query": "查询收入"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("text/event-stream"))
        self.assertEqual(response.text, "".join(events))
        self.server.run_stream.assert_called_once_with("查询收入")

    def test_stream_endpoint_validates_request(self) -> None:
        response = self.client.post("/api/v1/query/stream", json={})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error_type"], "request_validation")


if __name__ == "__main__":
    unittest.main()
