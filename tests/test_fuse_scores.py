import sys
import unittest
from pathlib import Path

# 直接执行 tests/test_fuse_scores.py 时，将项目根目录加入模块搜索路径。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag_retriever import fuse_scores


def hit(table: str, field: str, distance: float) -> dict:
    return {
        "distance": distance,
        "entity": {"field_name": field, "from_table": table},
    }


def index_by_field(results: list[dict]) -> dict[tuple[str, str], dict]:
    return {(item["table"], item["field"]): item for item in results}


class FuseScoresTests(unittest.TestCase):
    def test_union_and_formula(self) -> None:
        embedding_hits = [
            [
                hit("sales_orders", "net_amount", 0.8),
                hit("dim_customers", "region", 0.6),
            ]
        ]
        rule_hits = [
            {
                "whitelist": [{"table": "sales_orders", "field": "net_amount"}],
                "blacklist": [{"table": "sales_orders", "field": "gross_amount"}],
            }
        ]

        results = fuse_scores(embedding_hits, rule_hits)

        self.assertEqual(len(results), 3)
        self.assertEqual(
            [(item["table"], item["field"]) for item in results],
            [
                ("sales_orders", "net_amount"),
                ("dim_customers", "region"),
                ("sales_orders", "gross_amount"),
            ],
        )

        by_field = index_by_field(results)

        net = by_field[("sales_orders", "net_amount")]
        self.assertAlmostEqual(net["embedding_score"], 0.8)
        self.assertAlmostEqual(net["rule_score"], 1.0)
        self.assertAlmostEqual(net["final_score"], 0.7 * 0.8 + 0.3 * 1)

        region = by_field[("dim_customers", "region")]
        self.assertAlmostEqual(region["embedding_score"], 0.6)
        self.assertAlmostEqual(region["rule_score"], 0.0)
        self.assertAlmostEqual(region["final_score"], 0.42)

        gross = by_field[("sales_orders", "gross_amount")]
        self.assertAlmostEqual(gross["embedding_score"], 0.0)
        self.assertAlmostEqual(gross["rule_score"], -1.0)
        self.assertAlmostEqual(gross["final_score"], -0.3)

    def test_whitelist_and_blacklist_conflict_cancels_out(self) -> None:
        embedding_hits = [
            [hit("sales_orders", "net_amount", 0.5)]
        ]
        rule_hits = [
            {
                "whitelist": [{"table": "sales_orders", "field": "net_amount"}],
                "blacklist": [],
            },
            {
                "whitelist": [],
                "blacklist": [{"table": "sales_orders", "field": "net_amount"}],
            },
        ]

        results = fuse_scores(embedding_hits, rule_hits)

        self.assertEqual(len(results), 1)
        item = results[0]
        self.assertAlmostEqual(item["rule_score"], 0.0)
        self.assertAlmostEqual(item["final_score"], 0.7 * 0.5)

    def test_alpha_zero_uses_embedding_only(self) -> None:
        embedding_hits = [
            [
                hit("sales_orders", "net_amount", 0.8),
                hit("dim_customers", "region", 0.6),
                hit("sales_orders", "gross_amount", 0.4),
            ]
        ]
        rule_hits = [
            {
                "whitelist": [{"table": "sales_orders", "field": "net_amount"}],
                "blacklist": [{"table": "sales_orders", "field": "gross_amount"}],
            }
        ]

        results = fuse_scores(embedding_hits, rule_hits, alpha=0)

        self.assertEqual(
            [item["field"] for item in results],
            ["net_amount", "region", "gross_amount"],
        )
        self.assertAlmostEqual(results[0]["final_score"], 0.8)
        self.assertAlmostEqual(results[2]["final_score"], 0.4)

    def test_returns_empty_list_for_empty_inputs(self) -> None:
        self.assertEqual(fuse_scores([], []), [])

    def test_result_items_have_expected_fields(self) -> None:
        embedding_hits = [[hit("sales_orders", "net_amount", 0.8)]]
        rule_hits = [
            {
                "whitelist": [{"table": "sales_orders", "field": "net_amount"}],
                "blacklist": [],
            }
        ]

        for item in fuse_scores(embedding_hits, rule_hits):
            self.assertEqual(
                set(item),
                {
                    "table",
                    "field",
                    "embedding_score",
                    "rule_score",
                    "final_score",
                },
            )
            self.assertIsInstance(item["embedding_score"], float)
            self.assertIsInstance(item["rule_score"], float)
            self.assertIsInstance(item["final_score"], float)

    def test_duplicate_embedding_hits_keep_highest_and_rule_only_field(self) -> None:
        embedding_hits = [
            [
                hit("sales_orders", "net_amount", 0.2),
                hit("sales_orders", "net_amount", 0.9),
            ]
        ]
        rule_hits = [
            {
                "whitelist": [],
                "blacklist": [{"table": "sales_orders", "field": "gross_amount"}],
            }
        ]

        by_field = index_by_field(fuse_scores(embedding_hits, rule_hits))

        self.assertAlmostEqual(
            by_field[("sales_orders", "net_amount")]["embedding_score"], 0.9
        )
        self.assertAlmostEqual(
            by_field[("sales_orders", "gross_amount")]["embedding_score"], 0.0
        )

    def test_accepts_flat_hit_list(self) -> None:
        embedding_hits = [hit("sales_orders", "net_amount", 0.5)]

        results = fuse_scores(embedding_hits, [])

        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0]["embedding_score"], 0.5)


    def test_top_k_limits_to_best_scores(self) -> None:
        embedding_hits = [
            [
                hit("sales_orders", "net_amount", 0.8),
                hit("dim_customers", "region", 0.6),
                hit("sales_orders", "quantity", 0.4),
            ]
        ]

        results = fuse_scores(embedding_hits, [], top_k=2)

        self.assertEqual(
            [(item["table"], item["field"]) for item in results],
            [("sales_orders", "net_amount"), ("dim_customers", "region")],
        )

    def test_top_k_applies_after_rule_boost(self) -> None:
        embedding_hits = [
            [
                hit("dim_customers", "region", 0.6),
                hit("sales_orders", "net_amount", 0.5),
            ]
        ]
        rule_hits = [
            {
                "whitelist": [{"table": "sales_orders", "field": "net_amount"}],
                "blacklist": [],
            }
        ]

        results = fuse_scores(embedding_hits, rule_hits, top_k=1)

        # net_amount: 0.7*0.5+0.3*1=0.65 > region: 0.7*0.6=0.42
        self.assertEqual(
            [(item["table"], item["field"]) for item in results],
            [("sales_orders", "net_amount")],
        )

    def test_top_k_larger_than_results_returns_all(self) -> None:
        embedding_hits = [[hit("sales_orders", "net_amount", 0.8)]]

        self.assertEqual(len(fuse_scores(embedding_hits, [], top_k=10)), 1)

    def test_top_k_none_returns_all(self) -> None:
        embedding_hits = [
            [
                hit("sales_orders", "net_amount", 0.8),
                hit("dim_customers", "region", 0.6),
            ]
        ]

        self.assertEqual(len(fuse_scores(embedding_hits, [])), 2)


    def test_rule_hit_fields_always_kept_even_beyond_top_k(self) -> None:
        embedding_hits = [
            [
                hit("dim_customers", "region", 0.9),
                hit("sales_orders", "region", 0.8),
                hit("sales_orders", "net_amount", 0.1),
            ]
        ]
        rule_hits = [
            {
                "whitelist": [{"table": "sales_orders", "field": "net_amount"}],
                "blacklist": [{"table": "sales_orders", "field": "gross_amount"}],
            }
        ]

        results = fuse_scores(embedding_hits, rule_hits, top_k=1)

        # top_k=1 只留向量最高分那条，但两个规则命中字段必须补进来
        self.assertEqual(
            [(item["table"], item["field"]) for item in results],
            [
                ("dim_customers", "region"),
                ("sales_orders", "net_amount"),
                ("sales_orders", "gross_amount"),
            ],
        )

    def test_conflict_cancelled_field_still_treated_as_rule_hit(self) -> None:
        embedding_hits = [[hit("dim_customers", "region", 0.9)]]
        rule_hits = [
            {
                "whitelist": [{"table": "sales_orders", "field": "net_amount"}],
                "blacklist": [],
            },
            {
                "whitelist": [],
                "blacklist": [{"table": "sales_orders", "field": "net_amount"}],
            },
        ]

        results = fuse_scores(embedding_hits, rule_hits, top_k=1)

        # rule_score 抵消成 0，但它仍算被规则命中，必须保留
        keys = {(item["table"], item["field"]) for item in results}
        self.assertIn(("sales_orders", "net_amount"), keys)

    def test_top_k_still_applies_when_no_rule_hits(self) -> None:
        embedding_hits = [
            [
                hit("dim_customers", "region", 0.9),
                hit("sales_orders", "region", 0.8),
            ]
        ]

        results = fuse_scores(embedding_hits, [], top_k=1)

        self.assertEqual(
            [(item["table"], item["field"]) for item in results],
            [("dim_customers", "region")],
        )


if __name__ == "__main__":
    unittest.main()
