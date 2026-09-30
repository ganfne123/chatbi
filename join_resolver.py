"""意图识别最小 MVP：用 json_schema 约束 LLM 输出，把 query 归到 anchor / dimension / fuzzy。"""

import json
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from openai import OpenAI

from config import llm_config

load_dotenv()

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
        model=os.getenv("LLM_MODEL") or llm_config["model"],
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


if __name__ == "__main__":
    for q in ["按客户类型统计收入", "列出所有客户", "哪些客户没有下过订单",
              "各产品线的毛利率", "查询汇率历史", "看看最近的情况"]:
        print(f"{q}\n  {recognize_intent(q)}\n")
