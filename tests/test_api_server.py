import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import api_server


class APIServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_server = api_server.bi_server
        self.server = Mock()
        self.server.database = Mock()
        self.server.llm_client = Mock()
        api_server.bi_server = self.server
        self.client = TestClient(
            api_server.app,
            raise_server_exceptions=False,
        )

    def tearDown(self) -> None:
        api_server.bi_server = self.original_server

    def test_health_check_returns_service_status(self) -> None:
        self.server.database.health_check.return_value = True
        self.server.llm_client.health_check.return_value = True

        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "success": True,
                "database_health": True,
                "llm_health": True,
            },
        )

    def test_query_returns_success_response(self) -> None:
        self.server.run.return_value = {
            "success": True,
            "question": "收入",
            "sql": "SELECT 1",
            "columns": ["value"],
            "formatted": "value\n1",
            "metadata": {"total_ms": 10.0},
        }

        response = self.client.post(
            "/api/v1/query",
            json={"query": "收入"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["success"], True)
        self.assertEqual(body["sql"], "SELECT 1")
        self.assertEqual(body["formatted"], "value\n1")
        self.assertEqual(body["metadata"]["total_ms"], 10.0)

    def test_query_maps_validation_failure_to_400(self) -> None:
        self.server.run.return_value = {
            "success": False,
            "error": "输入问题为空",
            "error_type": "validation",
        }

        response = self.client.post(
            "/api/v1/query",
            json={"query": " "},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "success": False,
                "error": "输入问题为空",
                "error_type": "http_exception",
            },
        )

    def test_query_rejects_invalid_body(self) -> None:
        response = self.client.post("/api/v1/query", json={})

        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error_type"], "request_validation")


if __name__ == "__main__":
    unittest.main()
