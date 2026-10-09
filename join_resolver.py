"""意图识别最小 MVP：用 json_schema 约束 LLM 输出，把 query 归到 anchor / dimension / fuzzy。"""

import json
import os
from dataclasses import dataclass, field

from openai import OpenAI

from config import llm_config
from collections import deque
from json_schema.table_relationships import TABLE_RELATIONSHIPS
from rag_retriever import ClientMilvus


ANCHOR, DIMENSION, FUZZY = "anchor", "dimension", "fuzzy"

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
    table_type: str                                        # anchor / dimension / fuzzy
    is_fuzzy: bool
    reason: str
    fuzzy_fields: list[str] = field(default_factory=list)  # 仅 fuzzy 时有意义


def recognize_intent(query: str) -> IntentResult:
    """调用 LLM 识别查询意图，返回值由 INTENT_SCHEMA 保证结构。"""
    client = OpenAI(api_key=llm_config["api_key"], base_url=llm_config["base_url"])
    response = client.chat.completions.create(
        model=llm_config["model"],
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": f"待识别的用户查询：{query}"}],
        temperature=0,
        response_format=INTENT_SCHEMA,
    )
    data = json.loads(response.choices[0].message.content)

    return IntentResult(
        query=query,
        table_type=data["table_type"],
        is_fuzzy=data["table_type"] == FUZZY,
        reason=data["reason"],
        fuzzy_fields=data["fuzzy_fields"],
    )

def table_sort(table_scorse: list)->list:
    """对召回的内容按照分数排序"""
    # sorted_tables = sorted(table_scorse, key=lambda x: x["score"], reverse=True)
    return table_scorse

def anchor_table(table_scorse: list, intent_result: IntentResult):
    """根据意图识别结果，选出评分最高的表当锚表"""
    if intent_result.table_type == ANCHOR:
        table_scorse_sort=table_sort(table_scorse)
        for tables in table_scorse_sort:
            for table in tables:
                if table["entity"]["domain"] == "维度表":
                    return table["entity"]

    elif intent_result.table_type == DIMENSION:
        table_scorse_sort=table_sort(table_scorse)
        for tables in table_scorse_sort:
            for table in tables:
                if table["entity"]["domain"] == "dimension":
                    return table["entity"]

    else:
        # 意图模糊时，选子图中心性最高的表
        # return most_central_table(candidate_tables)
        return " TRUE"
    return " TRUE"

#广度优先算法
def find_path(start_node, end_node, table_relationships=TABLE_RELATIONSHIPS)->list:
    # 创建双端队列
    queue = deque([(start_node,[start_node])])
    # 创建一个集合来存储已访问的节点
    visited = {start_node}
    while len(queue) > 0:
        current_node, path = queue.popleft()
        if current_node == end_node:
            print(f"{current_node} 找到路径{path}")
            break
        for key,value in table_relationships.items():
            if key != current_node: 
                continue
            for relationship in value:
                target_node = relationship["target"]
                if target_node in visited:
                    continue
                visited.add(target_node)
                new_path = path + [target_node]
                queue.append((target_node,new_path))
                if target_node == end_node:
                    return new_path
    return []

def splicing_join(path: list)->str:
    """根据路径拼接 join 语句"""
    table_relationships=TABLE_RELATIONSHIPS
    # 处理路径中的每一对表，保存生成 join 语句
    join_statements=[]
    for i, anchor_path in enumerate(path[:-1]):
        for table in table_relationships[anchor_path]:
            if table["target"] == path[i + 1]:
                #  处理复合键的情况
                if len(table.get("fk_col",""))>1 and len(table.get("pk_col",""))>1:
                    fk_cols = table["fk_col"].split(",")
                    pk_cols = table["pk_col"].split(",")
                    join_conditions = [f"{anchor_path}.{fk}={table['target']}.{pk}" for fk, pk in zip(fk_cols, pk_cols)]
                    join_condition_str = " AND ".join(join_conditions)
                    join_statements.append(f"{anchor_path} {table['join_type']} {table['target']} on {join_condition_str}")
                else:
                    #  处理单键的情况
                    join_statements.append(f"{anchor_path} {table['join_type']} {table['target']} on {anchor_path}.{table['fk_col']}={table['target']}.{table['pk_col']}")
                continue
    return " ".join(join_statements)
    


def fetch_join_run(self, query: str):
    client = ClientMilvus()
    for q in ["按客户类型统计收入"]:
            #   "各产品线的毛利率", "查询汇率历史", "看看最近的情况":
        intent_result = recognize_intent(q)
        table_recall=client.table_search(
            query=q,
            collection_name=client.COLLECTION_TABLE_NAME,
            top_k=5,
        )
    anchor_table_result = anchor_table(table_recall, intent_result)
    for tables in table_recall:
        for table in tables:
            if table["entity"]["table_name"] != anchor_table_result["table_name"]:
                recall_table_relationships =[]
                table_name=table["entity"]["table_name"]
                table_path = find_path(start_node=anchor_table_result["table_name"], end_node=table_name, table_relationships=TABLE_RELATIONSHIPS)
                recall_table_relationships.append((table_name, table_path))
                join_sql = splicing_join(table_path)
                if join_sql:
                    return (f"锚表：{anchor_table_result['table_name']}，召回表：{table_name}，路径：{table_path}，join语句：{join_sql}")
                else:
                    return (f"锚表：{anchor_table_result['table_name']}，召回表：{table_name}，路径：{table_path}，无法生成 join 语句")