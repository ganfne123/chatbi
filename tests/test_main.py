import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

import pymysql
from openai import OpenAIError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import (
    ChatBiInternalError,
    ChatBiSystem,
    DatabaseServiceError,
    LLMServiceError,
    QueryValidationError,
)


class ChatBiSystemErrorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = ChatBiSystem.__new__(ChatBiSystem)
        self.system.query_parse = Mock()
        self.system.llm_client = Mock()
        self.system.database = Mock()
        self.system.result_formater = Mock()
        self.system.query_parse.parse.return_value = {"is_valid": True}
        self.system.query_parse.validate.return_value = True

    def test_invalid_query_raises_validation_error(self) -> None:
        self.system.query_parse.validate.return_value = False

        with self.assertRaises(QueryValidationError):
            self.system.run(" ")

    def test_llm_error_is_wrapped(self) -> None:
        self.system.llm_client.generate_sql.side_effect = OpenAIError("llm failed")

        with self.assertRaises(LLMServiceError) as context:
            self.system.run("收入")

        self.assertEqual(context.exception.error_type, "llm_error")
        self.assertEqual(context.exception.message, "大模型调用失败")
        self.assertEqual(
            context.exception.metadata["exception_type"],
            "OpenAIError",
        )

    def test_database_error_is_wrapped(self) -> None:
        self.system.llm_client.generate_sql.return_value = "SELECT 1"
        self.system.database.execute.side_effect = pymysql.MySQLError(
            "database failed"
        )

        with self.assertRaises(DatabaseServiceError) as context:
            self.system.run("收入")

        self.assertEqual(context.exception.error_type, "database_error")
        self.assertEqual(context.exception.message, "数据库查询失败")

    def test_formatter_error_is_wrapped(self) -> None:
        self.system.llm_client.generate_sql.return_value = "SELECT 1"
        self.system.database.execute.return_value = (["value"], [(1,)])
        self.system.result_formater.format.side_effect = RuntimeError(
            "format failed"
        )

        with self.assertRaises(ChatBiInternalError) as context:
            self.system.run("收入")

        self.assertEqual(
            context.exception.error_type,
            "internal_server_error",
        )

    def test_success_returns_normalized_result(self) -> None:
        self.system.llm_client.generate_sql.return_value = "SELECT 1"
        self.system.database.execute.return_value = (["value"], [(1,)])
        self.system.result_formater.format.return_value = "value\n1"

        result = self.system.run("收入")

        self.assertEqual(
            result,
            {
                "success": True,
                "sql": "SELECT 1",
                "columns": ["value"],
                "results": [(1,)],
                "formatted": "value\n1",
                "metadata": {},
            },
        )


if __name__ == "__main__":
    unittest.main()
