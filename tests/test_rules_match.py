import sys
import unittest
from pathlib import Path

# 直接执行 tests/test_rules_match.py 时，将项目根目录加入模块搜索路径。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rules_match import match_rules, parse_field


class ParseFieldTests(unittest.TestCase):
    def test_splits_table_and_field(self) -> None:
        self.assertEqual(
            parse_field("sales_orders.net_amount"),
            {"table": "sales_orders", "field": "net_amount"},
        )

    def test_field_without_table(self) -> None:
        self.assertEqual(parse_field("region"), {"table": None, "field": "region"})


class RulesMatchTests(unittest.TestCase):
    def test_revenue_rule_returns_whitelist_and_blacklist(self) -> None:
        results = match_rules("查询各大区的销售额")

        self.assertEqual(
            results,
            [
                {
                    "whitelist": [{"table": "sales_orders", "field": "net_amount"}],
                    "blacklist": [{"table": "sales_orders", "field": "gross_amount"}],
                }
            ],
        )

    def test_tax_and_revenue_rules_both_match(self) -> None:
        results = match_rules("含税收入是多少")

        self.assertEqual(
            results,
            [
                {
                    "whitelist": [{"table": "sales_orders", "field": "net_amount"}],
                    "blacklist": [{"table": "sales_orders", "field": "gross_amount"}],
                },
                {
                    "whitelist": [{"table": "sales_orders", "field": "gross_amount"}],
                    "blacklist": [{"table": "sales_orders", "field": "net_amount"}],
                },
            ],
        )

    def test_one_entry_per_rule_even_if_multiple_keywords_hit(self) -> None:
        # 收入 和 销售额 都属于同一条规则，命中多个触发词也只记一次。
        results = match_rules("收入和销售额")

        self.assertEqual(len(results), 1)

    def test_returns_empty_list_when_nothing_matches(self) -> None:
        self.assertEqual(match_rules("库存周转率是多少"), [])

    def test_returns_empty_list_for_empty_query(self) -> None:
        self.assertEqual(match_rules(""), [])

    def test_rejects_non_string_query(self) -> None:
        with self.assertRaises(TypeError):
            match_rules(None)  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            match_rules(123)  # type: ignore[arg-type]

    def test_result_items_have_expected_fields(self) -> None:
        for item in match_rules("含税收入是多少"):
            self.assertEqual(set(item), {"whitelist", "blacklist"})
            for entry in item["whitelist"] + item["blacklist"]:
                self.assertEqual(set(entry), {"table", "field"})
                self.assertTrue(entry["field"])


if __name__ == "__main__":
    unittest.main()
