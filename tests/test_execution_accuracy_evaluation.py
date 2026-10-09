#!/usr/bin/env python3
"""按课程 PDF 的 Execution Accuracy 逻辑评估 40 条 Text2SQL 用例。

核心判定完全对应 PDF 附录中的 Evaluator：

1. 加载测试用例；
2. 调用 SQL 生成器；
3. 分别执行预期 SQL 与生成 SQL；
4. 检查行数；
5. 普通字段比较字段名，聚合字段和派生指标只比较值；
6. 生成 SQL 可以包含额外字段，但不能缺少标准 SQL 的必需字段；
7. 忽略行顺序，汇总 Execution Accuracy 与 Exact Match Accuracy。

运行：

    uv run tests/test_execution_accuracy_evaluation.py

强制项目 LLM 重新生成全部 SQL：

    uv run tests/test_execution_accuracy_evaluation.py --force-generate
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Callable, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import DatabaseClient
from llm_client import LlmClient


CASE_PATH = Path(__file__).resolve().parent / "data" / "text2sql_eval_40.json"
REPORT_PATH = (
    Path(__file__).resolve().parent / "reports" / "execution_accuracy_40_report.txt"
)
SQL_CACHE_PATH = Path(__file__).resolve().parent / "reports" / "generated_sql_40.json"


class Evaluator:
    """SQL 生成评估器。"""

    def __init__(self, db_client: Optional[DatabaseClient] = None):
        self.db = db_client or DatabaseClient()

    def load_test_cases(self, path: str | Path = CASE_PATH) -> list[dict]:
        """从 JSON 文件加载测试用例。"""
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def evaluate_one(
        self,
        case: dict,
        sql_generator: Callable[[str], str],
    ) -> dict:
        """评估单个测试用例。"""
        question = case["question"]
        expected_sql = case["expected_sql"]

        result = {
            "id": case.get("id", "unknown"),
            "category": case.get("category", "unknown"),
            "question": question,
            "expected_sql": expected_sql,
            "generated_sql": None,
            "exact_match": False,
            "execution_match": False,
            "error": None,
            "detail": {},
        }

        # 1. 生成 SQL
        try:
            generated_sql = sql_generator(question)
            result["generated_sql"] = generated_sql
            result["exact_match"] = self._normalize_sql(
                generated_sql
            ) == self._normalize_sql(expected_sql)
        except Exception as exc:
            result["error"] = f"SQL 生成失败：{exc}"
            return result

        # 2. 执行预期 SQL 获取基准结果
        try:
            exp_columns, exp_results = self.db.execute(expected_sql)
        except Exception as exc:
            result["error"] = f"预期 SQL 执行失败：{exc}"
            return result

        # 3. 执行生成 SQL 获取结果
        try:
            gen_columns, gen_results = self.db.execute(generated_sql)
        except Exception as exc:
            result["error"] = f"生成 SQL 执行失败：{exc}"
            result["detail"] = {
                "expected_columns": exp_columns,
                "expected_row_count": len(exp_results),
            }
            return result

        # 4. 对比执行结果
        result["execution_match"] = self._results_equivalent(
            gen_columns,
            gen_results,
            generated_sql,
            exp_columns,
            exp_results,
            expected_sql,
        )
        result["detail"] = {
            "expected_columns": exp_columns,
            "expected_row_count": len(exp_results),
            "generated_columns": gen_columns,
            "generated_row_count": len(gen_results),
        }
        return result

    def evaluate_all(
        self,
        cases: list[dict],
        sql_generator: Callable[[str], str],
    ) -> list[dict]:
        """批量评估所有测试用例。"""
        return [self.evaluate_one(case, sql_generator) for case in cases]

    def generate_report(self, results: list[dict]) -> str:
        """生成文字评估报告。"""
        total = len(results)
        execution_correct = sum(1 for item in results if item["execution_match"])
        exact_correct = sum(1 for item in results if item["exact_match"])
        error_count = sum(1 for item in results if item["error"] is not None)

        categories: dict[str, dict[str, int]] = {}
        for item in results:
            category = item["category"]
            if category not in categories:
                categories[category] = {"total": 0, "correct": 0, "error": 0}
            categories[category]["total"] += 1
            if item["execution_match"]:
                categories[category]["correct"] += 1
            if item["error"]:
                categories[category]["error"] += 1

        lines = [
            "=" * 60,
            "ChatBI Text2SQL 评估报告",
            "=" * 60,
            f"总用例数：{total}",
            (
                f"Execution Accuracy：{execution_correct}/{total} = "
                f"{execution_correct / total * 100:.1f}%"
            ),
            (
                f"Exact Match Accuracy：{exact_correct}/{total} = "
                f"{exact_correct / total * 100:.1f}%"
            ),
            f"执行失败数：{error_count}",
            "",
            "按难度分类统计：",
        ]

        # PDF 示例只列出 simple/medium/complex；本项目实际使用 medium/hard，
        # 因此保留 PDF 顺序，并补上 hard。
        for category in ["simple", "medium", "hard", "complex"]:
            if category not in categories:
                continue
            stat = categories[category]
            accuracy = stat["correct"] / stat["total"] * 100 if stat["total"] else 0
            lines.append(
                f" {category:8s}: {stat['correct']}/{stat['total']} = "
                f"{accuracy:.1f}% (失败 {stat['error']})"
            )

        lines.extend(["", "详细结果："])
        for item in results:
            status = (
                "通过"
                if item["execution_match"]
                else ("失败" if item["error"] else "不匹配")
            )
            lines.append(f"\n[{item['id']}] {item['category']:8s} | {status}")
            lines.append(f" 问题：{item['question']}")
            if item["error"]:
                lines.append(f" 错误：{item['error']}")
            else:
                lines.append(f" 生成 SQL：{item['generated_sql'][:80]}...")
                if not item["execution_match"]:
                    lines.append(
                        f" 预期行数："
                        f"{item['detail'].get('expected_row_count', 'N/A')}, "
                        f"生成行数："
                        f"{item['detail'].get('generated_row_count', 'N/A')}"
                    )
        return "\n".join(lines)

    def _normalize_sql(self, sql: str) -> str:
        """标准化 SQL 字符串，用于 Exact Match 比较。"""
        return " ".join(sql.lower().split())

    def _results_equivalent(
        self,
        gen_columns: list,
        gen_results: list,
        gen_sql: str,
        exp_columns: list,
        exp_results: list,
        exp_sql: str,
    ) -> bool:
        """按字段类型比较标准 SQL 和生成 SQL 的结果。

        - 普通字段：必须存在同名字段。
        - 聚合字段、派生指标、窗口字段：忽略别名，只比较值。
        - 生成 SQL 的额外字段允许存在，但标准字段不能缺失。
        - 行顺序不影响判断。
        """
        del gen_sql  # 当前规则只使用标准 SQL 判断字段类型。
        if len(gen_results) != len(exp_results):
            return False

        expected_items = self._extract_select_items(exp_sql)
        derived_aliases = self._extract_derived_aliases(exp_sql)
        if len(expected_items) != len(exp_columns):
            # SQL 过于复杂无法可靠拆分时，保守地按字段名比较。
            expected_types = ["simple"] * len(exp_columns)
        else:
            expected_types = []
            for column_name, item in zip(exp_columns, expected_items):
                if not self._is_simple_field(item):
                    expected_types.append("value")
                elif str(column_name).strip().lower() in derived_aliases:
                    expected_types.append("value")
                else:
                    expected_types.append("simple")

        normalized_generated_names = [
            str(column).strip().lower() for column in gen_columns
        ]
        expected_rows = sorted(
            tuple(str(value) for value in row)
            for row in exp_results
        )

        # 为每个标准字段寻找候选生成字段。
        candidates: list[list[int]] = []
        for index, (column_name, field_type) in enumerate(
            zip(exp_columns, expected_types)
        ):
            if field_type == "simple":
                normalized_name = str(column_name).strip().lower()
                field_candidates = [
                    generated_index
                    for generated_index, generated_name in enumerate(
                        normalized_generated_names
                    )
                    if generated_name == normalized_name
                ]
            else:
                expected_values = sorted(
                    str(row[index]) for row in exp_results
                )
                field_candidates = [
                    generated_index
                    for generated_index in range(len(gen_columns))
                    if sorted(
                        str(row[generated_index]) for row in gen_results
                    )
                    == expected_values
                ]

            if not field_candidates:
                return False
            candidates.append(field_candidates)

        # 标准字段不能缺失，也不能重复映射到同一个生成字段。
        mapping: list[int] = []
        used_generated_indexes: set[int] = set()

        def match_columns(expected_index: int) -> bool:
            if expected_index == len(expected_types):
                projected_generated_rows = sorted(
                    tuple(str(row[generated_index]) for generated_index in mapping)
                    for row in gen_results
                )
                return projected_generated_rows == expected_rows

            for generated_index in candidates[expected_index]:
                if generated_index in used_generated_indexes:
                    continue
                used_generated_indexes.add(generated_index)
                mapping.append(generated_index)
                if match_columns(expected_index + 1):
                    return True
                mapping.pop()
                used_generated_indexes.remove(generated_index)
            return False

        return match_columns(0)

    def _extract_derived_aliases(self, sql: str) -> set[str]:
        """提取由函数或计算表达式定义的 CTE/派生字段别名。"""
        derived_aliases: set[str] = set()
        function_pattern = re.compile(
            r"(?is)\b(?:SUM|COUNT|AVG|MAX|MIN|DATE_FORMAT|LAG|LEAD|"
            r"RANK|DENSE_RANK|ROW_NUMBER)\s*\(.*?\bAS\s+"
            r"(?:`([^`]+)`|([A-Za-z_][A-Za-z0-9_$]*))"
        )
        for match in function_pattern.finditer(sql):
            alias = match.group(1) or match.group(2)
            derived_aliases.add(alias.strip().lower())

        # 识别 CTE 中不包含聚合函数、但由普通表达式计算出的字段。
        alias_pattern = re.compile(
            r"(?is)([A-Za-z_][A-Za-z0-9_$.]*\s*[-+*/]\s*"
            r"[A-Za-z_][A-Za-z0-9_$.]*)\s+AS\s+"
            r"(?:`([^`]+)`|([A-Za-z_][A-Za-z0-9_$]*))"
        )
        for match in alias_pattern.finditer(sql):
            alias = match.group(2) or match.group(3)
            derived_aliases.add(alias.strip().lower())
        return derived_aliases

    def _extract_select_items(self, sql: str) -> list[str]:
        """提取最外层最终 SELECT 的字段表达式列表。"""
        if not sql:
            return []

        select_positions: list[int] = []
        depth = 0
        quote: str | None = None
        index = 0
        while index < len(sql):
            char = sql[index]
            if quote is not None:
                if char == "\\" and quote != "`":
                    index += 2
                    continue
                if char == quote:
                    if index + 1 < len(sql) and sql[index + 1] == quote:
                        index += 2
                        continue
                    quote = None
                index += 1
                continue

            if char in ("'", '"', "`"):
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif depth == 0 and sql[index : index + 6].upper() == "SELECT":
                before = sql[index - 1] if index else " "
                after_index = index + 6
                after = sql[after_index] if after_index < len(sql) else " "
                if not (before.isalnum() or before == "_") and not (
                    after.isalnum() or after == "_"
                ):
                    select_positions.append(index)
                    index += 6
                    continue
            index += 1

        if not select_positions:
            return []

        start = select_positions[-1] + len("SELECT")
        depth = 0
        quote = None
        from_index: int | None = None
        index = start
        while index < len(sql):
            char = sql[index]
            if quote is not None:
                if char == "\\" and quote != "`":
                    index += 2
                    continue
                if char == quote:
                    if index + 1 < len(sql) and sql[index + 1] == quote:
                        index += 2
                        continue
                    quote = None
                index += 1
                continue

            if char in ("'", '"', "`"):
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif depth == 0 and sql[index : index + 4].upper() == "FROM":
                before = sql[index - 1] if index else " "
                after_index = index + 4
                after = sql[after_index] if after_index < len(sql) else " "
                if not (before.isalnum() or before == "_") and not (
                    after.isalnum() or after == "_"
                ):
                    from_index = index
                    break
            index += 1

        if from_index is None:
            return []

        clause = sql[start:from_index]
        items: list[str] = []
        current: list[str] = []
        depth = 0
        quote = None
        index = 0
        while index < len(clause):
            char = clause[index]
            if quote is not None:
                current.append(char)
                if char == "\\" and quote != "`":
                    if index + 1 < len(clause):
                        current.append(clause[index + 1])
                        index += 2
                        continue
                elif char == quote:
                    if index + 1 < len(clause) and clause[index + 1] == quote:
                        current.append(clause[index + 1])
                        index += 2
                        continue
                    quote = None
            elif char in ("'", '"', "`"):
                quote = char
                current.append(char)
            elif char == "(":
                depth += 1
                current.append(char)
            elif char == ")":
                depth = max(0, depth - 1)
                current.append(char)
            elif char == "," and depth == 0:
                item = "".join(current).strip()
                if item:
                    items.append(item)
                current = []
            else:
                current.append(char)
            index += 1

        final_item = "".join(current).strip()
        if final_item:
            items.append(final_item)
        return items

    @staticmethod
    def _is_simple_field(select_item: str) -> bool:
        """判断 SELECT 项是否是普通字段，而不是聚合或派生表达式。"""
        expression = re.split(
            r"\s+AS\s+", select_item, maxsplit=1, flags=re.IGNORECASE
        )[0].strip()
        identifier = r"(?:`[^`]+`|[A-Za-z_][A-Za-z0-9_$]*)"
        return re.fullmatch(
            rf"{identifier}(?:\.{identifier})*",
            expression,
        ) is not None

    def _should_check_column_names(self, sql: str) -> bool:
        """按 PDF 规则判断是否需要检查列名。"""
        if not sql:
            return True

        sql_upper = sql.upper()

        # 提取 SELECT 子句（到第一个 FROM 为止）
        match = re.search(r"SELECT\s+(.*?)(?:\s+FROM\s+)", sql_upper, re.DOTALL)
        if not match:
            return True

        select_clause = match.group(1).strip()

        # 按逗号分割 SELECT 项，考虑嵌套括号
        items = []
        depth = 0
        current = []
        for char in select_clause:
            if char == "(":
                depth += 1
                current.append(char)
            elif char == ")":
                depth -= 1
                current.append(char)
            elif char == "," and depth == 0:
                items.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            items.append("".join(current).strip())

        # 检查每一项是否都是聚合函数调用或常量
        for item in items:
            # 去除 AS 别名
            item_clean = re.split(
                r"\s+AS\s+", item, maxsplit=1, flags=re.IGNORECASE
            )[0].strip()

            # 聚合函数调用
            if re.match(
                r"^\s*(?:COUNT|SUM|AVG|MAX|MIN)\s*\(",
                item_clean,
                re.IGNORECASE,
            ):
                continue
            # 纯数字常量
            if re.match(r"^[\d+\-]?[\d]*\.?[\d]*$", item_clean):
                continue
            # 字符串常量
            if re.match(r"^'[^']*'$", item_clean) or re.match(
                r'^"[^"]*"$', item_clean
            ):
                continue

            # 包含原始列引用或其他表达式，需要检查列名
            return True

        # 所有项都是聚合函数或常量，不检查列名
        return False


def _load_sql_cache() -> dict[str, str]:
    if not SQL_CACHE_PATH.exists():
        return {}
    with SQL_CACHE_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return {
        str(case_id): item["generated_sql"]
        for case_id, item in data.get("cases", {}).items()
        if item.get("generated_sql")
    }


def _save_sql_cache(cases: list[dict], generated_by_id: dict[str, str]) -> None:
    SQL_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "case_count": len(cases),
            "model": __import__("os").getenv("LLM_MODEL", ""),
        },
        "cases": {
            str(case["id"]): {
                "generated_sql": generated_by_id[str(case["id"])],
                "error": None,
            }
            for case in cases
            if str(case["id"]) in generated_by_id
        },
    }
    SQL_CACHE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_sql_generator(
    cases: list[dict],
    *,
    force_generate: bool = False,
) -> Callable[[str], str]:
    """构造注入评估器的 SQL 生成函数。"""
    cached = {} if force_generate else _load_sql_cache()
    generated_by_id = {str(case["id"]): cached.get(str(case["id"])) for case in cases}
    case_id_by_question = {case["question"]: str(case["id"]) for case in cases}
    llm = LlmClient()

    def generate_sql(question: str) -> str:
        case_id = case_id_by_question[question]
        cached_sql = generated_by_id.get(case_id)
        if cached_sql:
            return cached_sql

        raw_sql = llm.generate_sql(question)
        generated_sql = llm.sql_parse(raw_sql).strip()
        generated_by_id[case_id] = generated_sql
        _save_sql_cache(cases, generated_by_id)
        return generated_sql

    return generate_sql


def run_evaluation(
    test_cases_path: str | Path = CASE_PATH,
    *,
    force_generate: bool = False,
) -> str:
    """运行完整评估流程并返回 PDF 格式的文字报告。"""
    evaluator = Evaluator()
    cases = evaluator.load_test_cases(test_cases_path)
    sql_generator = build_sql_generator(cases, force_generate=force_generate)
    results = evaluator.evaluate_all(cases, sql_generator)
    report = evaluator.generate_report(results)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report + "\n", encoding="utf-8")
    print(report)
    print(f"\n报告文件：{REPORT_PATH}")
    return report


class EvaluatorTest(unittest.TestCase):
    """评估器单元测试，不请求 LLM，不连接真实数据库。"""

    class FakeDatabase:
        def __init__(self, results: dict[str, tuple[list[str], list[tuple]]]):
            self.results = results

        def execute(self, sql: str):
            return self.results[sql]

    def test_ignores_row_order(self) -> None:
        expected = "SELECT country FROM dim_customers"
        generated = "SELECT country FROM dim_customers"
        database = self.FakeDatabase(
            {expected: (["country"], [("China",), ("USA",)])}
        )
        case = {
            "id": 1,
            "category": "medium",
            "question": "国家",
            "expected_sql": expected,
        }

        result = Evaluator(database).evaluate_one(case, lambda question: generated)

        self.assertTrue(result["execution_match"])

    def test_pure_aggregate_ignores_column_alias(self) -> None:
        expected = "SELECT SUM(net_amount) AS total FROM sales_orders"
        generated = "SELECT SUM(net_amount) AS revenue FROM sales_orders"
        database = self.FakeDatabase(
            {
                expected: (["total"], [(100,)]),
                generated: (["revenue"], [(100,)]),
            }
        )
        case = {
            "id": 2,
            "category": "medium",
            "question": "收入",
            "expected_sql": expected,
        }

        result = Evaluator(database).evaluate_one(case, lambda question: generated)

        self.assertTrue(result["execution_match"])

    def test_generated_extra_columns_are_allowed_when_required_columns_exist(self) -> None:
        expected = "SELECT product_name FROM dim_products"
        generated = "SELECT product_id, product_name, material_cost FROM dim_products"
        database = self.FakeDatabase(
            {
                expected: (["product_name"], [("产品A",), ("产品B",)]),
                generated: (
                    ["product_id", "product_name", "material_cost"],
                    [(2, "产品B", 20), (1, "产品A", 10)],
                ),
            }
        )
        case = {
            "id": 4,
            "category": "medium",
            "question": "产品",
            "expected_sql": expected,
        }

        result = Evaluator(database).evaluate_one(case, lambda question: generated)

        self.assertTrue(result["execution_match"])

    def test_mixed_query_ignores_aggregate_alias(self) -> None:
        expected = "SELECT product_name, SUM(amount) AS revenue FROM sales"
        generated = "SELECT product_name, SUM(amount) AS sales_revenue FROM sales"
        database = self.FakeDatabase(
            {
                expected: (["product_name", "revenue"], [("产品A", 100), ("产品B", 200)]),
                generated: (
                    ["product_name", "sales_revenue"],
                    [("产品B", 200), ("产品A", 100)],
                ),
            }
        )
        case = {
            "id": 6,
            "category": "medium",
            "question": "产品收入",
            "expected_sql": expected,
        }

        result = Evaluator(database).evaluate_one(case, lambda question: generated)

        self.assertTrue(result["execution_match"])

    def test_mixed_query_ignores_derived_metric_alias(self) -> None:
        expected = (
            "SELECT product_name, SUM(amount) - SUM(cost) AS gross_profit "
            "FROM sales"
        )
        generated = (
            "SELECT product_name, SUM(amount) - SUM(cost) AS profit "
            "FROM sales"
        )
        database = self.FakeDatabase(
            {
                expected: (["product_name", "gross_profit"], [("产品A", 50)]),
                generated: (["product_name", "profit"], [("产品A", 50)]),
            }
        )
        case = {
            "id": 7,
            "category": "medium",
            "question": "产品毛利",
            "expected_sql": expected,
        }

        result = Evaluator(database).evaluate_one(case, lambda question: generated)

        self.assertTrue(result["execution_match"])

    def test_generated_extra_columns_fail_when_required_column_is_missing(self) -> None:
        expected = "SELECT product_name, material_cost FROM dim_products"
        generated = "SELECT product_name, labor_cost FROM dim_products"
        database = self.FakeDatabase(
            {
                expected: (["product_name", "material_cost"], [("产品A", 10)]),
                generated: (["product_name", "labor_cost"], [("产品A", 5)]),
            }
        )
        case = {
            "id": 5,
            "category": "medium",
            "question": "产品成本",
            "expected_sql": expected,
        }

        result = Evaluator(database).evaluate_one(case, lambda question: generated)

        self.assertFalse(result["execution_match"])

    def test_non_aggregate_checks_column_names(self) -> None:
        expected = "SELECT country FROM dim_customers"
        generated = "SELECT country AS nation FROM dim_customers"
        database = self.FakeDatabase(
            {
                expected: (["country"], [("China",)]),
                generated: (["nation"], [("China",)]),
            }
        )
        case = {
            "id": 3,
            "category": "medium",
            "question": "国家",
            "expected_sql": expected,
        }

        result = Evaluator(database).evaluate_one(case, lambda question: generated)

        self.assertFalse(result["execution_match"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force-generate",
        action="store_true",
        help="忽略 SQL 缓存，重新调用项目 LLM 生成全部 SQL",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_evaluation(force_generate=args.force_generate)
