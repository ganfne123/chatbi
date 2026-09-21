"""指标知识检索模块。

根据用户 query 匹配指标名称或别名，并返回命中指标及其全部依赖指标。
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any


class IndicatorKnowledgeError(ValueError):
    """指标知识文件不存在、格式错误或依赖关系非法时抛出。"""


class IndicatorKnowledge:
    """从 JSON 配置中加载并检索指标知识。"""

    def __init__(self, knowledge_path: str | Path ="pormpt.json") -> None:
        """初始化检索器，加载并校验指标知识配置。

        Args:
            knowledge_path: 指标知识 JSON 文件路径。未提供时依次查找模块同目录
                和项目根目录下的 ``pormpt.json``。

        Raises:
            IndicatorKnowledgeError: 配置文件不可读、格式错误或依赖关系非法。
        """
        self.knowledge_path = (
            Path(knowledge_path)
            
        )
        self._indicators = self._load_indicators()
        self._validate_indicator_fields()
        self._indicators_by_name = {
            indicator["name"]: indicator for indicator in self._indicators
        }
        self._validate_indicators()



    def get_knowledge(self, query: str) -> list[dict[str, Any]]:
        """返回 query 命中的指标及其递归依赖。

        Args:
            query: 需要匹配指标名称或别名的用户查询。

        Returns:
            按依赖项优先顺序排列的指标深拷贝列表；未命中时返回空列表。

        Raises:
            TypeError: query 不是字符串。
        """
        if not isinstance(query, str):
            raise TypeError("query 必须是字符串")
        if not query:
            return []

        matched_names = [
            indicator["name"]
            for indicator in self._indicators
            if self._matches_indicator(query, indicator)
        ]

        resolved_names: list[str] = []
        resolved_name_set: set[str] = set()

        def add_with_dependencies(name: str) -> None:
            """递归加入指标及其依赖，确保依赖项先于当前指标。"""
            if name in resolved_name_set:
                return

            for dependency_name in self._indicators_by_name[name]["depends_on"]:
                add_with_dependencies(dependency_name)

            resolved_name_set.add(name)
            resolved_names.append(name)

        for matched_name in matched_names:
            add_with_dependencies(matched_name)

        return [
            copy.deepcopy(self._indicators_by_name[name]) for name in resolved_names
        ]

    def _load_indicators(self) -> list[dict[str, Any]]:
        """读取 JSON 文件并返回其中的原始指标列表。

        Returns:
            JSON 中 ``indicators`` 字段对应的指标对象列表。

        Raises:
            IndicatorKnowledgeError: 文件不可读、JSON 非法或顶层结构错误。
        """
        try:
            with self.knowledge_path.open("r", encoding="utf-8") as file:
                config = json.load(file)
        except OSError as exc:
            raise IndicatorKnowledgeError(
                f"无法读取指标知识文件 {self.knowledge_path}: {exc}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise IndicatorKnowledgeError(
                f"指标知识文件 {self.knowledge_path} 不是合法 JSON "
                f"(第 {exc.lineno} 行，第 {exc.colno} 列): {exc.msg}"
            ) from exc

        if not isinstance(config, dict) or not isinstance(
            config.get("indicators"), list
        ):
            raise IndicatorKnowledgeError(
                f"指标知识文件 {self.knowledge_path} 的 indicators 必须是列表"
            )

        indicators = config["indicators"]
        if not all(isinstance(indicator, dict) for indicator in indicators):
            raise IndicatorKnowledgeError("indicators 中的每一项都必须是对象")

        return indicators

    def _validate_indicator_fields(self) -> None:
        """校验每个指标的 name、aliases 和 depends_on 字段。

        Raises:
            IndicatorKnowledgeError: 任一必需字段缺失或类型不符合要求。
        """
        for indicator in self._indicators:
            name = indicator.get("name")
            aliases = indicator.get("aliases")
            dependencies = indicator.get("depends_on")

            if not isinstance(name, str) or not name.strip():
                raise IndicatorKnowledgeError("每个指标的 name 必须是非空字符串")
            if not isinstance(aliases, list) or not all(
                isinstance(alias, str) and alias.strip() for alias in aliases
            ):
                raise IndicatorKnowledgeError(
                    f"指标 {name!r} 的 aliases 必须是非空字符串列表"
                )
            if not isinstance(dependencies, list) or not all(
                isinstance(dependency, str) and dependency.strip()
                for dependency in dependencies
            ):
                raise IndicatorKnowledgeError(
                    f"指标 {name!r} 的 depends_on 必须是字符串列表"
                )

    def _validate_indicators(self) -> None:
        """校验指标名称唯一性及 depends_on 引用是否有效。

        Raises:
            IndicatorKnowledgeError: 指标名称重复或依赖指标不存在。
        """
        if len(self._indicators_by_name) != len(self._indicators):
            raise IndicatorKnowledgeError("指标 name 不能重复")

        for indicator in self._indicators:
            name = indicator["name"]
            dependencies = indicator["depends_on"]
            missing_dependencies = [
                dependency
                for dependency in dependencies
                if dependency not in self._indicators_by_name
            ]
            if missing_dependencies:
                raise IndicatorKnowledgeError(
                    f"指标 {name!r} 引用了不存在的依赖指标: "
                    f"{', '.join(missing_dependencies)}"
                )

        self._validate_dependency_cycles()

    def _validate_dependency_cycles(self) -> None:
        """使用深度优先遍历检测指标依赖环。

        Raises:
            IndicatorKnowledgeError: depends_on 关系存在循环。
        """
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(name: str) -> None:
            """访问单个指标节点，并在发现回边时报告循环依赖。"""
            if name in visiting:
                raise IndicatorKnowledgeError(f"指标依赖存在循环: {name}")
            if name in visited:
                return

            visiting.add(name)
            for dependency_name in self._indicators_by_name[name]["depends_on"]:
                visit(dependency_name)
            visiting.remove(name)
            visited.add(name)

        for indicator in self._indicators:
            visit(indicator["name"])

    @staticmethod
    def _matches_indicator(query: str, indicator: dict[str, Any]) -> bool:
        """判断 query 是否包含指标名称或任一别名。

        Args:
            query: 用户查询。
            indicator: 包含 name 和 aliases 的指标对象。

        Returns:
            名称或任一别名命中时返回 True，否则返回 False。
        """
        terms = [indicator["name"], *indicator["aliases"]]
        return any(IndicatorKnowledge._matches_term(query, term) for term in terms)

    @staticmethod
    def _matches_term(query: str, term: str) -> bool:
        """按中英文规则判断单个指标词是否出现在 query 中。

        中文词使用直接子串匹配；英文词使用忽略大小写的整词匹配。

        Args:
            query: 用户查询。
            term: 指标名称或别名。

        Returns:
            匹配成功时返回 True，否则返回 False。
        """
        if term.isascii() and any(character.isalnum() for character in term):
            pattern = (
                rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])"
            )
            return re.search(pattern, query, flags=re.IGNORECASE) is not None

        return term in query


# def main() -> None:
#     """交互式查看 query 命中的指标及其完整依赖链路。"""
#     query = input("请输入查询: ").strip()

#     try:
#         indicators = IndicatorKnowledge().get_knowledge(query)
#     except IndicatorKnowledgeError as exc:
#         print(f"加载指标知识失败: {exc}")
#         return

#     if not indicators:
#         print("未匹配到任何指标。")
#         return

#     print("\n依赖展开顺序：")
#     for index, indicator in enumerate(indicators, start=1):
#         dependencies = indicator.get("depends_on", [])
#         dependency_text = "、".join(dependencies) if dependencies else "无"
#         print(f"{index}. {indicator['name']}（依赖：{dependency_text}）")

#     print("\n完整指标知识：")
#     print(json.dumps(indicators, ensure_ascii=False, indent=2))


# if __name__ == "__main__":
#     main()
