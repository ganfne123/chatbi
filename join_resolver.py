"""
Join 路径推理：
1. 意图识别，选出锚表（通常是事实表）
2. 以锚表为根，在表关系图上求连通所有必需表的最小边集（BFS 生成树）
3. 按边去重后生成 JOIN 语句，避免多表场景重复 JOIN
"""

import json
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field

from openai import OpenAI

from config import llm_config
from json_schema.table_relationships import TABLE_RELATIONSHIPS


ANCHOR, DIMENSION, FUZZY = "anchor", "dimension", "fuzzy"
FACT_DOMAINS = {"事实表", "fact"}
DIMENSION_DOMAINS = {"维度表", "dimension"}

SYSTEM_PROMPT = """你是数据分析系统的查询意图识别模块，判断用户查询属于哪种表类型。

- anchor（锚表/事实表）：业务主体是可聚合的数值指标（收入、销售额、费用、毛利、利润、金额、数量）
- dimension（维度表）：业务主体是具体实体对象（客户、产品、订单、汇率）
- fuzzy（模糊字段）：判断不出来就选它，不要猜表类型"""


# 结构化输出：用 json_schema 把返回值锁死，table_type 只能是三个枚举值之一
INTENT_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "intent_result",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "table_type": {"type": "string", "enum": [ANCHOR, DIMENSION, FUZZY]},
                "reason": {"type": "string"},
                "fuzzy_fields": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["table_type", "reason", "fuzzy_fields"],
            "additionalProperties": False,
        },
    },
}


@dataclass
class IntentResult:
    query: str
    table_type: str
    is_fuzzy: bool
    reason: str
    fuzzy_fields: list[str] = field(default_factory=list)


# ==================== 意图识别 ====================

def recognize_intent(query: str) -> IntentResult:
    """调用 LLM 识别查询意图，返回值由 INTENT_SCHEMA 保证结构。"""
    client = OpenAI(api_key=llm_config["api_key"], base_url=llm_config["base_url"])
    # 注意：部分 OpenAI 兼容网关（如当前 deepseek 网关）不支持 json_schema，
    # 只支持 json_object，因此这里用 json_object 并把格式要求写进 system prompt。
    json_hint = (
        "\n只输出一个 JSON 对象，不要输出任何解释，格式为："
        '{"table_type":"anchor|dimension|fuzzy","reason":"...","fuzzy_fields":[]}'
    )
    response = client.chat.completions.create(
        model=llm_config["model"],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + json_hint},
            {"role": "user", "content": f"待识别的用户查询：{query}"},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("大模型意图识别失败")
    data = json.loads(content)

    return IntentResult(
        query=query,
        table_type=data["table_type"],
        is_fuzzy=data["table_type"] == FUZZY,
        reason=data["reason"],
        fuzzy_fields=data["fuzzy_fields"],
    )


# ==================== 召回结果解析 ====================

def _iter_hits(table_recall: list):
    """兼容 Milvus 的 [[hit, ...]] 嵌套结构，也兼容扁平的 [hit, ...]。"""
    for layer in table_recall or []:
        hits = layer if isinstance(layer, list) else [layer]
        for hit in hits:
            yield hit


def _referenced_tables(table_recall: list) -> list[str]:
    """提取召回结果里的表名，去重且保持召回顺序。"""
    names: list[str] = []
    for hit in _iter_hits(table_recall):
        name = hit.get("entity", {}).get("table_name")
        if name and name not in names:
            names.append(name)
    return names


# ==================== 表关系图 ====================

def _invert_join_type(join_type: str) -> str:
    """反向遍历关系图时，LEFT/RIGHT JOIN 需要互换。"""
    normalized = re.sub(r"\s+", " ", str(join_type).strip().upper())
    mapping = {
        "LEFT JOIN": "RIGHT JOIN",
        "RIGHT JOIN": "LEFT JOIN",
        "LEFT OUTER JOIN": "RIGHT OUTER JOIN",
        "RIGHT OUTER JOIN": "LEFT OUTER JOIN",
    }
    return mapping.get(normalized, join_type)


def _build_adjacency(table_relationships: dict | None = None) -> dict[str, list[tuple[str, dict]]]:
    """把有向的表关系配置展开成无向邻接表。

    每个邻接项是 (邻居表, 边信息)，边信息里的 fk_col 属于当前表、
    pk_col 属于邻居表，保证从任意方向都能正确生成 JOIN 条件。
    """
    relationships = table_relationships or TABLE_RELATIONSHIPS
    adjacency: dict[str, list[tuple[str, dict]]] = defaultdict(list)

    for source, relations in relationships.items():
        adjacency.setdefault(source, [])
        for relation in relations:
            target = relation["target"]
            adjacency[source].append(
                (
                    target,
                    {
                        "join_type": relation["join_type"],
                        "fk_col": relation["fk_col"],
                        "pk_col": relation["pk_col"],
                    },
                )
            )
            adjacency.setdefault(target, []).append(
                (
                    source,
                    {
                        "join_type": _invert_join_type(relation["join_type"]),
                        "fk_col": relation["pk_col"],
                        "pk_col": relation["fk_col"],
                    },
                )
            )

    return adjacency


def _join_condition(left: str, right: str, edge: dict) -> str:
    """生成 left JOIN right 的条件，支持复合键。"""
    fk_cols = [col.strip() for col in str(edge["fk_col"]).split(",") if col.strip()]
    pk_cols = [col.strip() for col in str(edge["pk_col"]).split(",") if col.strip()]
    if not fk_cols or len(fk_cols) != len(pk_cols):
        raise ValueError(f"非法关联配置：{left} -> {right}, {edge}")

    conditions = [f"{left}.{fk} = {right}.{pk}" for fk, pk in zip(fk_cols, pk_cols)]
    return f"{left} {edge['join_type']} {right} ON " + " AND ".join(conditions)


# ==================== 锚表选择 ====================

def table_sort(table_scorse: list) -> list:
    """对召回的内容按照分数排序。"""
    return table_scorse


def anchor_table(table_recall: list, intent_result: IntentResult) -> str:
    """根据意图识别结果选出锚表；找不到指定类型时退化为“最中心表”。"""
    if not table_recall:
        return ""

    if intent_result.table_type == ANCHOR:
        for hit in _iter_hits(table_recall):
            entity = hit.get("entity", {})
            if entity.get("domain") in FACT_DOMAINS:
                return entity["table_name"]

    elif intent_result.table_type == DIMENSION:
        for hit in _iter_hits(table_recall):
            entity = hit.get("entity", {})
            if entity.get("domain") in DIMENSION_DOMAINS:
                return entity["table_name"]

    return _most_central_table(table_recall)


def _most_central_table(table_recall: list) -> str:
    """选与其他召回表距离总和最小的表作为锚表。"""
    tables = _referenced_tables(table_recall)
    if not tables:
        return ""

    scores: list[tuple[str, int]] = []
    for current_table in tables:
        distance_sum = 0
        for other_table in tables:
            if other_table == current_table:
                continue
            path = bfs_find_path(current_table, other_table)
            distance_sum += 99 if not path else len(path) - 1
        scores.append((current_table, distance_sum))

    return min(scores, key=lambda item: (item[1], item[0]))[0]


# ==================== 路径搜索 ====================

def bfs_find_path(start_node, end_node, table_relationships=TABLE_RELATIONSHIPS) -> list:
    """在表关系图上做 BFS，返回 start -> end 的最短路径（表名列表）。"""
    if start_node == end_node:
        return [start_node]

    adjacency = _build_adjacency(table_relationships)
    if start_node not in adjacency:
        return []

    queue = deque([(start_node, [start_node])])
    visited = {start_node}

    while queue:
        current_node, path = queue.popleft()
        for neighbor, _edge in adjacency.get(current_node, []):
            if neighbor in visited:
                continue
            new_path = path + [neighbor]
            if neighbor == end_node:
                return new_path
            visited.add(neighbor)
            queue.append((neighbor, new_path))

    return []


# ==================== 最小连通子图 ====================

def build_join_plan(
    anchor: str,
    required_tables: list[str],
    table_relationships: dict | None = None,
) -> dict:
    """以 anchor 为根，构造连通所有必需表的最小生成树。

    返回：
        anchor:       锚表
        order:        生成 JOIN 的顺序（锚表在前）
        parent:       子表 -> 父表
        edges:        子表 -> 连到父表所用的边信息
        paths:        目标表 -> 到锚表的路径
        joins:        去重后的 JOIN 语句列表
        unreachable:  无法连通的表
    """
    adjacency = _build_adjacency(table_relationships)
    required = [table for table in dict.fromkeys(required_tables) if table != anchor]

    result = {
        "anchor": anchor,
        "order": [anchor] if anchor else [],
        "parent": {},
        "edges": {},
        "paths": {},
        "joins": [],
        "unreachable": [],
    }
    if not anchor or anchor not in adjacency:
        result["unreachable"] = required
        return result

    # 以锚表为根做一次 BFS，记录每个节点的父节点和通向父节点的边
    parent: dict[str, str] = {}
    parent_edge: dict[str, dict] = {}
    depth: dict[str, int] = {anchor: 0}
    visited = {anchor}
    queue = deque([anchor])

    while queue:
        current = queue.popleft()
        for neighbor, edge in adjacency.get(current, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = current
            parent_edge[neighbor] = edge
            depth[neighbor] = depth[current] + 1
            queue.append(neighbor)

    # 只保留“目标表到锚表路径上”的节点，避免把无关兄弟节点也 JOIN 进来
    needed_nodes: set[str] = {anchor}
    needed_edges: dict[str, dict] = {}

    for target in required:
        if target not in visited:
            result["unreachable"].append(target)
            continue

        path = [target]
        node = target
        while node != anchor:
            needed_nodes.add(node)
            needed_edges[node] = parent_edge[node]
            node = parent[node]
            path.append(node)

        result["paths"][target] = list(reversed(path))

    # 按层级排序，保证父表先于子表出现
    ordered_nodes = sorted(needed_nodes, key=lambda node: (depth[node], node))
    result["order"] = ordered_nodes

    for node in ordered_nodes:
        if node == anchor:
            continue
        left = parent[node]
        result["parent"][node] = left
        result["edges"][node] = needed_edges[node]
        result["joins"].append(_join_condition(left, node, needed_edges[node]))

    return result


def splicing_join(path: list) -> str:
    """根据路径拼接 JOIN 语句（保留原接口，供单路径调用）。"""
    if not path or len(path) < 2:
        return ""

    adjacency = _build_adjacency()
    statements: list[str] = []

    for left, right in zip(path, path[1:]):
        edge = next((edge for neighbor, edge in adjacency.get(left, []) if neighbor == right), None)
        if edge is None:
            continue
        statements.append(_join_condition(left, right, edge))

    return " ".join(statements)


def _format_join_plan(plan: dict) -> str:
    """把 join plan 格式化成可拼进 Prompt 的文本。"""
    lines = [f"锚表：{plan['anchor']}"]

    if plan["paths"]:
        lines.append("关联路径：")
        for target, path in plan["paths"].items():
            lines.append(f"- {target}：{' -> '.join(path)}")

    if plan["unreachable"]:
        lines.append("无法连通（不要强行 JOIN）：")
        lines.append("- " + "、".join(plan["unreachable"]))

    if plan["joins"]:
        lines.append("JOIN 语句：")
        lines.extend(plan["joins"])
    elif not plan["unreachable"]:
        lines.append("无需关联其他表")

    return "\n".join(lines)


# ==================== 对外入口 ====================

def fetch_join_run(query: str, table_recall: list) -> str:
    """选锚表 -> 求最小连通子图 -> 返回去重后的 JOIN 说明。"""
    recalled_tables = _referenced_tables(table_recall)
    if not recalled_tables:
        return ""

    try:
        intent_result = recognize_intent(query)
        anchor = anchor_table(table_recall, intent_result)
    except Exception:
        # 意图识别只是增强信息，失败时退化为“最中心表”，不阻断主链路
        anchor = _most_central_table(table_recall)

    if anchor not in recalled_tables:
        anchor = _most_central_table(table_recall)

    plan = build_join_plan(anchor, recalled_tables)
    return _format_join_plan(plan)


if __name__ == "__main__":
    demo_recall = [
        [
            {"entity": {"table_name": "sales_orders", "domain": "事实表"}},
            {"entity": {"table_name": "dim_customers", "domain": "维度表"}},
            {"entity": {"table_name": "dim_products", "domain": "维度表"}},
        ]
    ]
    print(fetch_join_run("查询各客户类型的产品销售额", demo_recall))
