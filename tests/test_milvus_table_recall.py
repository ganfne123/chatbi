#!/usr/bin/env python3
"""Milvus 表召回评估。

测试集共 40 条问题。每条问题包含 required_tables，表示该问题必须召回的
真实业务表。集合中前 5 张表是真实表，其余表是干扰表。

运行：

    uv run tests/test_milvus_table_recall.py

并发数可按环境调整：

    uv run tests/test_milvus_table_recall.py --workers 4
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from json_schema.table_scheam import TABLE_METADATA
from rag_retriever import ClientMilvus


CASE_PATH = Path(__file__).resolve().parent / "data" / "milvus_table_recall_40.json"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
JSON_REPORT_PATH = REPORT_DIR / "milvus_table_recall_40_latest.json"
MARKDOWN_REPORT_PATH = REPORT_DIR / "milvus_table_recall_40_report.md"
TOP_K = 4

# TABLE_METADATA 是 {表名: 表描述} 的有序字典，前 5 张为真实表，其余为干扰表
TABLE_NAMES = tuple(TABLE_METADATA)
SEARCH_LIMIT = len(TABLE_NAMES)
REAL_TABLES = TABLE_NAMES[:5]
DISTRACTOR_TABLES = TABLE_NAMES[5:]


class TableRecallEvaluator:
    """计算表召回排名、得分和命中指标。"""

    def __init__(
        self,
        search: Callable[[str, int], list[dict[str, Any]]],
        *,
        top_k: int = TOP_K,
    ) -> None:
        self.search = search
        self.top_k = top_k

    def evaluate_case(self, case: dict[str, Any]) -> dict[str, Any]:
        results = self.search(case["question"], SEARCH_LIMIT)
        ranked = sorted(
            [
                {
                    "rank": index,
                    "table_name": item["table_name"],
                    "score": float(item["score"]),
                }
                for index, item in enumerate(results, start=1)
            ],
            key=lambda item: item["score"],
            reverse=True,
        )
        for index, item in enumerate(ranked, start=1):
            item["rank"] = index

        required_tables = [str(item) for item in case["required_tables"]]
        required_set = set(required_tables)
        top_k = ranked[: self.top_k]
        top_k_names = [item["table_name"] for item in top_k]
        hit_tables = [name for name in required_tables if name in top_k_names]
        missing_tables = [name for name in required_tables if name not in top_k_names]

        first_required_rank = None
        for item in ranked:
            if item["table_name"] in required_set:
                first_required_rank = item["rank"]
                break

        annotated_results = []
        for item in ranked:
            table_name = item["table_name"]
            is_required = table_name in required_set
            is_real = table_name in REAL_TABLES
            if is_required:
                marker = "必须召回"
            elif is_real:
                marker = "真实表-非必需"
            else:
                marker = "干扰表"
            annotated_results.append(
                {
                    **item,
                    "is_required": is_required,
                    "is_real": is_real,
                    "marker": marker,
                    "in_top_k": item["rank"] <= self.top_k,
                }
            )

        recall = len(hit_tables) / len(required_tables) if required_tables else 0.0
        reciprocal_rank = 1.0 / first_required_rank if first_required_rank else 0.0
        return {
            "id": case["id"],
            "category": case.get("category", "unknown"),
            "question": case["question"],
            "required_tables": required_tables,
            "top_k": self.top_k,
            "top_k_tables": top_k_names,
            "hit_required_tables": hit_tables,
            "missing_required_tables": missing_tables,
            "recall": recall,
            "all_required_recalled": not missing_tables,
            "reciprocal_rank": reciprocal_rank,
            "first_required_rank": first_required_rank,
            "distractor_count_in_top_k": sum(
                item["table_name"] in DISTRACTOR_TABLES for item in top_k
            ),
            "results": annotated_results,
        }

    def summarize(self, case_results: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(case_results)
        return {
            "case_count": total,
            "top_k": self.top_k,
            "mean_recall_at_k": round(
                sum(item["recall"] for item in case_results) / total * 100, 1
            )
            if total
            else 0.0,
            "all_required_hit_rate": round(
                sum(item["all_required_recalled"] for item in case_results)
                / total
                * 100,
                1,
            )
            if total
            else 0.0,
            "mrr_at_k": round(
                sum(item["reciprocal_rank"] for item in case_results) / total, 4
            )
            if total
            else 0.0,
            "distractor_count_in_top_k": sum(
                item["distractor_count_in_top_k"] for item in case_results
            ),
            "required_table_stats": self._required_table_stats(case_results),
        }

    @staticmethod
    def _required_table_stats(
        case_results: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        stats = {
            table_name: {"required_cases": 0, "hit_cases": 0, "missing_cases": 0}
            for table_name in REAL_TABLES
        }
        for item in case_results:
            for table_name in item["required_tables"]:
                stats[table_name]["required_cases"] += 1
                if table_name in item["hit_required_tables"]:
                    stats[table_name]["hit_cases"] += 1
                else:
                    stats[table_name]["missing_cases"] += 1
        for values in stats.values():
            denominator = values["required_cases"]
            values["recall_percent"] = round(
                values["hit_cases"] / denominator * 100, 1
            ) if denominator else 0.0
        return stats


def _normalize_search_results(raw_results: Any) -> list[dict[str, Any]]:
    """兼容 MilvusClient.search 返回的 Hit 结构。"""
    results = []
    for item in raw_results:
        if isinstance(item, dict):
            table_name = item.get("table_name") or item.get("entity", {}).get(
                "table_name"
            )
            score = item.get("score", item.get("distance"))
        else:
            table_name = item.entity.get("table_name")
            score = item.distance
        if table_name is None or score is None:
            continue
        results.append({"table_name": str(table_name), "score": float(score)})
    return results


def _search_once(
    client: ClientMilvus,
    question: str,
    limit: int,
) -> list[dict[str, Any]]:
    embedding = client.embedding.get_embedding(question)
    raw = client.client.search(
        collection_name=client.COLLECTION_TABLE_NAME,
        data=[embedding],
        limit=limit,
        output_fields=["table_name", "domain", "page_content", "key_fields"],
    )
    return _normalize_search_results(raw[0] if raw else [])


def _search_with_retry(
    client: ClientMilvus,
    question: str,
    limit: int,
    attempts: int = 3,
) -> list[dict[str, Any]]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return _search_once(client, question, limit)
        except Exception as exc:  # noqa: BLE001 - retain failure for report
            last_error = exc
            if attempt < attempts:
                time.sleep(attempt)
    raise RuntimeError(f"{type(last_error).__name__}: {last_error}")


def _load_cases(path: Path = CASE_PATH) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        cases = json.load(file)
    if len(cases) != 40:
        raise ValueError(f"召回测试集必须包含 40 条，实际为 {len(cases)}")
    return cases


def _write_markdown_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Milvus 表召回测试报告",
        "",
        f"- 运行时间：{report['metadata']['generated_at']}",
        f"- 测试集：{report['metadata']['case_count']} 条",
        f"- 向量模型：`{report['metadata']['embedding_model']}`",
        f"- Top-K：{summary['top_k']}",
        f"- 真实表：{', '.join(REAL_TABLES)}",
        f"- 干扰表：{', '.join(DISTRACTOR_TABLES)}",
        "",
        "## 汇总指标",
        "",
        "| 指标 | 数值 |",
        "|---|---:|",
        f"| Mean Recall@K | {summary['mean_recall_at_k']:.1f}% |",
        f"| 全部必需表命中率 | {summary['all_required_hit_rate']:.1f}% |",
        f"| MRR@K | {summary['mrr_at_k']:.4f} |",
        f"| Top-K 干扰表总数 | {summary['distractor_count_in_top_k']} |",
        "",
        "## 逐表召回率",
        "",
        "| 表名 | 必需用例数 | Top-K 命中 | 漏召回 | 召回率 |",
        "|---|---:|---:|---:|---:|",
    ]
    for table_name, values in summary["required_table_stats"].items():
        lines.append(
            f"| `{table_name}` | {values['required_cases']} | "
            f"{values['hit_cases']} | {values['missing_cases']} | "
            f"{values['recall_percent']:.1f}% |"
        )

    lines.extend(["", "## 逐条结果", ""])
    for item in report["case_results"]:
        required = ", ".join(f"`{name}`" for name in item["required_tables"])
        hit = ", ".join(f"`{name}`" for name in item["hit_required_tables"]) or "无"
        missing = ", ".join(f"`{name}`" for name in item["missing_required_tables"]) or "无"
        status = "通过" if item["all_required_recalled"] else "漏召回"
        lines.extend(
            [
                f"### [{item['id']}] {item['question']}",
                "",
                f"- 状态：**{status}**",
                f"- 必须召回：{required}",
                f"- Top-{item['top_k']} 命中：{hit}",
                f"- 漏召回：{missing}",
                f"- Recall@{item['top_k']}：{item['recall'] * 100:.1f}%",
                f"- 首个必需表排名：{item['first_required_rank'] or '未命中'}",
                "",
                "| 排名 | 表名 | 得分 | 类型 | Top-K |",
                "|---:|---|---:|---|---|",
            ]
        )
        for result in item["results"]:
            lines.append(
                f"| {result['rank']} | `{result['table_name']}` | "
                f"{result['score']:.6f} | {result['marker']} | "
                f"{'是' if result['in_top_k'] else '否'} |"
            )
        lines.append("")

    MARKDOWN_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_recall_evaluation(
    *,
    case_path: Path = CASE_PATH,
    workers: int = 4,
    top_k: int = TOP_K,
) -> dict[str, Any]:
    cases = _load_cases(case_path)
    client = ClientMilvus()

    def search(question: str, limit: int) -> list[dict[str, Any]]:
        return _search_with_retry(client, question, limit)

    evaluator = TableRecallEvaluator(search, top_k=top_k)
    case_results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(evaluator.evaluate_case, case): case for case in cases
        }
        completed = 0
        for future in as_completed(futures):
            case = futures[future]
            try:
                case_result = future.result()
            except Exception as exc:  # noqa: BLE001 - preserve failed case in report
                case_result = {
                    "id": case["id"],
                    "category": case.get("category", "unknown"),
                    "question": case["question"],
                    "required_tables": case["required_tables"],
                    "top_k": top_k,
                    "top_k_tables": [],
                    "hit_required_tables": [],
                    "missing_required_tables": case["required_tables"],
                    "recall": 0.0,
                    "all_required_recalled": False,
                    "reciprocal_rank": 0.0,
                    "first_required_rank": None,
                    "distractor_count_in_top_k": 0,
                    "results": [],
                    "error": f"{type(exc).__name__}: {exc}",
                }
            case_results.append(case_result)
            completed += 1
            print(
                f"[{completed:02d}/{len(cases)}] {case['id']} "
                f"recall={case_result['recall'] * 100:.1f}%",
                flush=True,
            )

    case_results.sort(key=lambda item: int(item["id"]))
    summary = evaluator.summarize(case_results)
    report = {
        "metadata": {
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "case_count": len(cases),
            "embedding_model": os.getenv("EMBEDDING_MODEL_NAME", ""),
            "collection_name": client.COLLECTION_TABLE_NAME,
            "search_limit": SEARCH_LIMIT,
            "real_tables": list(REAL_TABLES),
            "distractor_tables": list(DISTRACTOR_TABLES),
        },
        "summary": summary,
        "case_results": case_results,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_markdown_report(report)

    print("\n" + "=" * 72)
    print("Milvus 表召回测试报告")
    print("=" * 72)
    print(f"Mean Recall@{top_k}：{summary['mean_recall_at_k']:.1f}%")
    print(f"全部必需表命中率：{summary['all_required_hit_rate']:.1f}%")
    print(f"MRR@{top_k}：{summary['mrr_at_k']:.4f}")
    print(f"Top-{top_k} 干扰表总数：{summary['distractor_count_in_top_k']}")
    print(f"JSON 报告：{JSON_REPORT_PATH}")
    print(f"Markdown 报告：{MARKDOWN_REPORT_PATH}")
    return report


class TableRecallEvaluatorTest(unittest.TestCase):
    """召回指标单元测试，不访问 Embedding 或 Milvus。"""

    @staticmethod
    def _results_with_required_in_top_five(question: str, limit: int):
        del question, limit
        return [
            {"table_name": "sales_orders", "score": 0.90},
            {"table_name": "dim_products", "score": 0.80},
            {"table_name": "exchange_rates", "score": 0.70},
            {"table_name": "website_logs", "score": 0.60},
            {"table_name": "weather_data", "score": 0.50},
            {"table_name": "dim_customers", "score": 0.40},
            {"table_name": "finance_expenses", "score": 0.30},
            {"table_name": "dim_employees", "score": 0.20},
            {"table_name": "hr_attendance", "score": 0.10},
            {"table_name": "it_assets", "score": 0.05},
            {"table_name": "office_supplies", "score": 0.01},
        ]

    def test_all_required_tables_hit_in_top_k(self) -> None:
        case = {
            "id": 13,
            "category": "medium",
            "question": "查询2025年每个产品的销售收入",
            "required_tables": [
                "sales_orders",
                "dim_products",
                "exchange_rates",
            ],
        }
        evaluator = TableRecallEvaluator(
            self._results_with_required_in_top_five,
            top_k=5,
        )

        result = evaluator.evaluate_case(case)

        self.assertEqual(
            result["hit_required_tables"],
            ["sales_orders", "dim_products", "exchange_rates"],
        )
        self.assertEqual(result["missing_required_tables"], [])
        self.assertTrue(result["all_required_recalled"])
        self.assertEqual(result["recall"], 1.0)
        self.assertEqual(result["first_required_rank"], 1)

    def test_missing_required_table_is_reported(self) -> None:
        def search(question: str, limit: int):
            del question, limit
            return [
                {"table_name": "sales_orders", "score": 0.90},
                {"table_name": "dim_products", "score": 0.80},
                {"table_name": "weblog", "score": 0.70},
                {"table_name": "hr_attendance", "score": 0.60},
                {"table_name": "weather_data", "score": 0.50},
                {"table_name": "exchange_rates", "score": 0.40},
            ] + [
                {"table_name": table_name, "score": 0.30 - index * 0.01}
                for index, table_name in enumerate(DISTRACTOR_TABLES)
            ]

        case = {
            "id": 1,
            "category": "medium",
            "question": "产品收入",
            "required_tables": ["sales_orders", "exchange_rates"],
        }
        result = TableRecallEvaluator(search, top_k=5).evaluate_case(case)

        self.assertEqual(result["hit_required_tables"], ["sales_orders"])
        self.assertEqual(result["missing_required_tables"], ["exchange_rates"])
        self.assertFalse(result["all_required_recalled"])
        self.assertAlmostEqual(result["recall"], 0.5)

    def test_summary_counts_required_table_coverage(self) -> None:
        case = {
            "id": 1,
            "category": "medium",
            "question": "产品收入",
            "required_tables": ["sales_orders", "dim_products"],
        }
        evaluator = TableRecallEvaluator(
            self._results_with_required_in_top_five,
            top_k=5,
        )
        result = evaluator.evaluate_case(case)

        summary = evaluator.summarize([result])

        self.assertEqual(summary["mean_recall_at_k"], 100.0)
        self.assertEqual(summary["all_required_hit_rate"], 100.0)
        self.assertEqual(
            summary["required_table_stats"]["sales_orders"]["recall_percent"],
            100.0,
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4, help="并发检索数")
    parser.add_argument("--top-k", type=int, default=TOP_K, help="Top-K")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_recall_evaluation(workers=args.workers, top_k=args.top_k)
