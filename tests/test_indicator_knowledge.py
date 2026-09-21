import json
import sys
import tempfile
import unittest
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path

# 直接执行 tests/test_indicator_knowledge.py 时，将项目根目录加入模块搜索路径。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from indicator_knowledge import (
    IndicatorKnowledge,
    IndicatorKnowledgeError,
)


class IndicatorKnowledgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.knowledge = IndicatorKnowledge()

    def names(self, query: str) -> list[str]:
        return [item["name"] for item in self.knowledge.get_knowledge(query)]

    def test_matches_chinese_name_and_aliases(self) -> None:
        self.assertEqual(self.names("今年收入是多少"), ["收入"])
        self.assertEqual(self.names("销售额同比如何"), ["收入"])
        self.assertEqual(self.names("查看营收"), ["收入"])

    def test_matches_english_aliases_case_insensitively(self) -> None:
        self.assertEqual(self.names("Show GROSS_PROFIT"), ["收入", "销售成本", "毛利"])
        self.assertEqual(self.names("profit trend"), ["收入", "销售成本", "毛利", "期间费用", "利润"])

    def test_english_matching_respects_word_boundaries(self) -> None:
        self.assertEqual(self.names("profitable orders"), [])
        self.assertEqual(self.names("gross_profit"), ["收入", "销售成本", "毛利"])

    def test_returns_empty_list_when_nothing_matches(self) -> None:
        self.assertEqual(self.knowledge.get_knowledge("库存周转率是多少"), [])
        self.assertEqual(self.knowledge.get_knowledge(""), [])

    def test_recursively_returns_all_dependencies_in_dependency_order(self) -> None:
        self.assertEqual(
            self.names("利润是多少"),
            ["收入", "销售成本", "毛利", "期间费用", "利润"],
        )

    def test_multiple_matches_are_merged_and_deduplicated(self) -> None:
        self.assertEqual(
            self.names("比较收入和利润"),
            ["收入", "销售成本", "毛利", "期间费用", "利润"],
        )
        self.assertEqual(len(self.names("毛利和利润")), 5)

    def test_returns_deep_copies(self) -> None:
        first_result = self.knowledge.get_knowledge("收入")
        first_result[0]["definition"] = "已被调用方修改"

        second_result = self.knowledge.get_knowledge("收入")
        self.assertNotEqual(second_result[0]["definition"], "已被调用方修改")

    def test_rejects_non_string_query(self) -> None:
        with self.assertRaises(TypeError):
            self.knowledge.get_knowledge(None)  # type: ignore[arg-type]

    def test_loads_from_custom_path(self) -> None:
        payload = {
            "indicators": [
                {
                    "name": "自定义指标",
                    "aliases": ["custom"],
                    "depends_on": [],
                }
            ]
        }
        with self._config_file(payload) as path:
            knowledge = IndicatorKnowledge(path)
            self.assertEqual(
                [item["name"] for item in knowledge.get_knowledge("custom指标")],
                ["自定义指标"],
            )

    def test_rejects_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.json"
            path.write_text("{not-json", encoding="utf-8")

            with self.assertRaisesRegex(IndicatorKnowledgeError, "不是合法 JSON"):
                IndicatorKnowledge(path)

    def test_rejects_invalid_structure(self) -> None:
        with self._config_file({"indicators": "not-a-list"}) as path:
            with self.assertRaisesRegex(IndicatorKnowledgeError, "indicators 必须是列表"):
                IndicatorKnowledge(path)

    def test_rejects_non_string_indicator_name(self) -> None:
        payload = {"indicators": [{"name": [], "aliases": [], "depends_on": []}]}
        with self._config_file(payload) as path:
            with self.assertRaisesRegex(IndicatorKnowledgeError, "name 必须是非空字符串"):
                IndicatorKnowledge(path)

    def test_rejects_duplicate_names(self) -> None:
        payload = {
            "indicators": [
                {"name": "重复指标", "aliases": [], "depends_on": []},
                {"name": "重复指标", "aliases": [], "depends_on": []},
            ]
        }
        with self._config_file(payload) as path:
            with self.assertRaisesRegex(IndicatorKnowledgeError, "name 不能重复"):
                IndicatorKnowledge(path)

    def test_rejects_missing_dependency(self) -> None:
        payload = {
            "indicators": [
                {"name": "利润", "aliases": [], "depends_on": ["不存在"]}
            ]
        }
        with self._config_file(payload) as path:
            with self.assertRaisesRegex(IndicatorKnowledgeError, "不存在的依赖指标"):
                IndicatorKnowledge(path)

    def test_rejects_dependency_cycle(self) -> None:
        payload = {
            "indicators": [
                {"name": "A", "aliases": [], "depends_on": ["B"]},
                {"name": "B", "aliases": [], "depends_on": ["A"]},
            ]
        }
        with self._config_file(payload) as path:
            with self.assertRaisesRegex(IndicatorKnowledgeError, "依赖存在循环"):
                IndicatorKnowledge(path)

    @staticmethod
    @contextmanager
    def _config_file(payload: dict) -> Iterator[Path]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "knowledge.json"
            path.write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            yield path


if __name__ == "__main__":
    unittest.main()
