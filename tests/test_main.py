import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

import pymysql
from openai import OpenAIError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import ChatBiSystem


class ChatBiSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = ChatBiSystem.__new__(ChatBiSystem)
        self.system.query_parse = Mock()
        self.system.llm_client = Mock()
        self.system.database = Mock()
        self.system.result_formater = Mock()
        self.system.query_parse.parse.return_value = {"is_valid": True}
        self.system.query_parse.validate.return_value = True

    def test_invalid_query_returns_validation_error(self) -> None:
        self.system.query_parse.validate.return_value = False

        result = self.system.run(" ")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error_type"], "validation")

    def test_llm_error_returns_generate_sql_error(self) -> None:
        self.system.llm_client.generate_sql.side_effect = OpenAIError("llm failed")

        result = self.system.run("收入")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error_type"], "generate_sql_error")

    def test_database_error_returns_database_error(self) -> None:
        self.system.llm_client.generate_sql.return_value = "SELECT 1"
        self.system.llm_client.sql_parse.return_value = "SELECT 1"
        self.system.database.execute.side_effect = pymysql.MySQLError(
            "database failed"
        )

        result = self.system.run("收入")

        self.assertEqual(result["success"], False)
        self.assertEqual(result["error_type"], "database_execute_error")

    def test_success_returns_timing_metadata(self) -> None:
        self.system.llm_client.generate_sql.return_value = "SELECT 1"
        self.system.llm_client.sql_parse.return_value = "SELECT 1"
        self.system.database.execute.return_value = (["value"], [(1,)])
        self.system.result_formater.format.return_value = "value\n1"

        result = self.system.run("收入")

        self.assertEqual(result["success"], True)
        self.assertEqual(result["sql"], "SELECT 1")
        self.assertGreaterEqual(result["metadata"]["sql_generation_ms"], 0)
        self.assertGreaterEqual(result["metadata"]["total_ms"], 0)


if __name__ == "__main__":
    unittest.main()
