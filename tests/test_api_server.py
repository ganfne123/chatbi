import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import api_server
from main import (
    ChatBiInternalError,
    DatabaseServiceError,
    LLMServiceError,
    QueryValidationError,
)


class APIServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_system = api_server.system
        self.system = Mock()
        self.system.database = Mock()
        api_server.system = self.system
        self.client = TestClient(
            api_server.app,
            raise_server_exceptions=False,
        )

    def tearDown(self) -> None:
        api_server.system = self.original_system

    def test_root_returns_service_links(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "name": "ChatBI MVP API",
                "docs": "/docs",
                "health": "/health",
                "query": "/api/v1/query",
            },
        )

    def test_health_check_reports_database_status(self) -> None:
        self.system.database.validate_connection.return_value = True
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "database_connected": True},
        )

        self.system.database.validate_connection.return_value = False
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "database_connected": False},
        )

    def test_query_returns_normalized_result(self) -> None:
        self.system.run.return_value = {
            "success": True,
            "sql": "SELECT SUM(net_amount) FROM sales_orders",
            "columns": ["total"],
            "results": [(100,)],
            "formatted": "total\n100",
            "metadata": {"source": "database"},
        }

        response = self.client.post(
            "/api/v1/query",
            json={"question": "  收入是多少  "},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["success"], True)
        self.assertEqual(body["question"], "收入是多少")
        self.assertEqual(body["sql"], "SELECT SUM(net_amount) FROM sales_orders")
        self.assertEqual(body["columns"], ["total"])
        self.assertEqual(body["rows"], [{"total": 100}])
        self.assertEqual(body["formatted"], "total\n100")
        self.assertEqual(body["metadata"]["source"], "database")
        self.assertGreaterEqual(body["metadata"]["duration_ms"], 0)
        self.system.run.assert_called_once_with("收入是多少")

    def test_query_rejects_invalid_request_body(self) -> None:
        for payload in ({}, {"question": ""}, {"question": 123}):
            with self.subTest(payload=payload):
                response = self.client.post("/api/v1/query", json=payload)
                self.assertEqual(response.status_code, 422)
                body = response.json()
                self.assertFalse(body["success"])
                self.assertEqual(body["error"], "请求参数校验失败")
                self.assertEqual(body["error_type"], "request_validation")
                self.assertEqual(body["metadata"]["path"], "/api/v1/query")

    def test_query_rejects_whitespace_only_question(self) -> None:
        response = self.client.post(
            "/api/v1/query",
            json={"question": "   "},
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], "输入问题不合法")
        self.assertEqual(body["error_type"], "validation_error")
        self.system.run.assert_not_called()

    def test_query_maps_validation_error_to_400(self) -> None:
        self.system.run.side_effect = QueryValidationError("输入问题不合法")

        response = self.client.post(
            "/api/v1/query",
            json={"question": "无效查询"},
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body["error"], "输入问题不合法")
        self.assertEqual(body["error_type"], "validation_error")
        self.assertEqual(body["metadata"]["path"], "/api/v1/query")

    def test_query_maps_llm_error_to_502(self) -> None:
        self.system.run.side_effect = LLMServiceError("大模型调用失败")

        response = self.client.post(
            "/api/v1/query",
            json={"question": "收入"},
        )

        self.assertEqual(response.status_code, 502)
        body = response.json()
        self.assertEqual(body["error"], "大模型调用失败")
        self.assertEqual(body["error_type"], "llm_error")

    def test_query_maps_database_error_to_500(self) -> None:
        self.system.run.side_effect = DatabaseServiceError("数据库查询失败")

        response = self.client.post(
            "/api/v1/query",
            json={"question": "收入"},
        )

        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertEqual(body["error"], "数据库查询失败")
        self.assertEqual(body["error_type"], "database_error")

    def test_query_maps_internal_error_to_500(self) -> None:
        self.system.run.side_effect = ChatBiInternalError("服务内部异常")

        response = self.client.post(
            "/api/v1/query",
            json={"question": "收入"},
        )

        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertEqual(body["error"], "服务内部异常")
        self.assertEqual(body["error_type"], "internal_server_error")

    def test_query_hides_unexpected_exception_details(self) -> None:
        self.system.run.side_effect = RuntimeError("secret traceback detail")

        response = self.client.post(
            "/api/v1/query",
            json={"question": "收入"},
        )

        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertEqual(body["success"], False)
        self.assertEqual(body["error"], "服务内部异常")
        self.assertEqual(body["error_type"], "internal_server_error")
        self.assertNotIn("secret", str(body))


if __name__ == "__main__":
    unittest.main()
