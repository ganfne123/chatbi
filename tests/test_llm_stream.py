import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm_client import LlmClient


class LlmStreamTests(unittest.TestCase):
    def setUp(self) -> None:
        self.llm = LlmClient.__new__(LlmClient)
        self.llm.client = Mock()
        self.llm.indicator_knowledge = Mock()
        self.llm.indicator_knowledge.get_knowledge.return_value = []

    def test_stream_skips_chunks_without_choices(self) -> None:
        chunks = [
            SimpleNamespace(choices=[]),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        delta=SimpleNamespace(content="SELECT"),
                    )
                ]
            ),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        delta=SimpleNamespace(content=None),
                    )
                ]
            ),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        delta=SimpleNamespace(content=" 1"),
                    )
                ]
            ),
        ]
        self.llm.client.chat.completions.create.return_value = iter(chunks)

        result = list(self.llm.generate_sql_stream("查询"))

        self.assertEqual(result, ["SELECT", " 1"])


if __name__ == "__main__":
    unittest.main()
