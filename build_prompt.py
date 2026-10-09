from typing import Any
SYSTEM_PROMPT = """你是一个数据分析助手，根据用户的自然语言查询生成对应的 MySQL SQL 语句。
要求：
1. 只输出一条可执行的 SQL 语句，不要输出任何解释或额外内容；
2. SQL 必须符合 MySQL 语法规范；
3. 不允许出现任何敏感信息；
4. 只生成查询类语句（SELECT/SHOW/EXPLAIN 等），不要生成 INSERT、UPDATE、DELETE、DROP 等写操作。"""


Schema="""
表：dim_customers
- customer_id int(11)
- customer_name varchar(100)
- customer_type varchar(50)
- industry varchar(50)
- country varchar(50)
- region varchar(50)

表：dim_products
- product_id int(11)
- product_name varchar(100)
- product_line varchar(50)
- category varchar(50)
- tech_route varchar(50)
- standard_cost decimal(10,2)
- material_cost decimal(10,2)
- labor_cost decimal(10,2)

表：exchange_rates
- rate_date date
- currency varchar(10)
- rate_to_cny decimal(10,4)

表：finance_expenses
- expense_id bigint(20)
- expense_date date
- department varchar(50)
- rd_expense decimal(12,2)
- selling_expense decimal(12,2)
- admin_expense decimal(12,2)
- finance_expense decimal(12,2)
- marketing_expense decimal(12,2)
- logistics_expense decimal(12,2)
- warranty_expense decimal(12,2)

表：sales_orders
- order_id bigint(20)
- order_no varchar(50)
- customer_id int(11) 外键 → dim_customers.customer_id
- product_id int(11) 外键 → dim_products.product_id
- region varchar(50)
- order_date date
- order_status varchar(20)
- quantity decimal(10,2)
- unit_price decimal(10,2)
- discount_amount decimal(10,2)
- gross_amount decimal(12,2)
- net_amount decimal(12,2)
- currency varchar(10)
"""

# ==================== Few-shot 示例 ====================
FEW_SHOT_EXAMPLES = """
示例1：
问题：查询已完成订单的总数量
SQL：SELECT COUNT(*) FROM sales_orders WHERE order_status = 'completed';

示例2：
问题：按客户类型统计订单数量
SQL：SELECT c.customer_type, COUNT(*) AS order_count FROM sales_orders o JOIN dim_customers c ON o.customer_id = c.customer_id WHERE o.order_status = 'completed' GROUP BY c.customer_type;

示例3：
问题：查询2026年第一季度的总费用
SQL：SELECT SUM(rd_expense + selling_expense + admin_expense + finance_expense) AS total_expense FROM finance_expenses WHERE expense_date >= '2026-01-01' AND expense_date < '2026-04-01';

示例4：
问题：查看最近三个月各月销售收入
SQL：SELECT
    DATE_FORMAT(o.order_date, '%Y-%m-01') AS month,
    SUM(o.net_amount * r.rate_to_cny) AS revenue_cny
FROM sales_orders o
JOIN exchange_rates r
  ON o.order_date = r.rate_date
 AND o.currency = r.currency
WHERE o.order_status = 'completed'
  AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
  AND o.order_date < CURDATE() + INTERVAL 1 DAY
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m-01')
ORDER BY month;
"""



# ==================== RAG 检索结果格式化 ====================
def format_schema_linking(schema_linking: dict | None) -> str:
    """把 run_schema_linking 的返回值格式化成可拼进 prompt 的文本。"""
    if not schema_linking:
        return ""

    lines: list[str] = []

    # 召回的表 + 每张表的 page_content
    tables = schema_linking.get("recalled_tables") or []
    table_page_content = schema_linking.get("table_page_content") or {}
    if tables:
        lines.append("召回的表：")
        for name in dict.fromkeys(tables):
            content = table_page_content.get(name) or ""
            line = f"- {name}"
            if content:
                line += f"：{content}"
            lines.append(line)

    # 召回的字段 + 每个字段的 page_content
    fields = schema_linking.get("fields") or []
    if fields:
        lines.append("召回/规则命中的字段（按相关度排序）：")
        seen: list[str] = []
        for item in fields:
            name = f"{item.get('table')}.{item.get('field')}"
            if name in seen:
                continue
            seen.append(name)
            content = item.get("page_content") or ""
            line = f"- {name}"
            if content:
                line += f"：{content}"
            lines.append(line)

    join_sql = schema_linking.get("join_sql")
    if join_sql:
        lines.append("表连接方式（join）：\n" + join_sql)

    return "\n".join(lines)


def format_indicators(indicators: list[dict] | None) -> str:
    """把 run_indicator_search 的返回值格式化成可拼进 prompt 的文本。"""
    if not indicators:
        return ""

    lines: list[str] = []
    for item in indicators:
        name = item.get("name") or ""
        level = item.get("level") or ""
        definition = item.get("definition") or ""
        line = f"- {name}"
        if level:
            line += f"（{level}）"
        if definition:
            line += f"：{definition}"
        lines.append(line)
    return "\n".join(lines)


def build_prompt(
    user_question: str,
    use_few_shot: bool = True,
    use_rules: bool = False,
    use_guards: bool = False,
    use_include_join: bool = False,
    use_schema_linking: bool = False,
) -> list:
    """组装最终发给大模型的消息。

    retrieval_context 由 rag_retriever.retrieve_context() 产出，结构：
    {
        "schema_linking": {recalled_tables, fields, join_sql, ...},
        "indicators": [{name, level, definition, score}, ...],
    }
    """
    system = f"{SYSTEM_PROMPT} "
    user = f"用户问题为：{user_question}\n"

    if use_few_shot:
        system += f"你可以参考以下示例：\n{FEW_SHOT_EXAMPLES}\n"


    # 把 RAG 检索结果拼进 system prompt
    if use_schema_linking:
        from rag_retriever import run_schema_linking
        schema_text = format_schema_linking(run_schema_linking(user_question))
        if schema_text:
            system += f"以下是检索到的相关表结构信息，生成 SQL 时请优先使用：\n{schema_text}\n"
    if use_include_join:
        from rag_retriever import run_indicator_search
        indicator_text = format_indicators(run_indicator_search(user_question))
        if indicator_text:
            system += f"以下是检索到的指标定义，计算口径请以此为准：\n{indicator_text}\n"

    message = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    return message


if __name__ == "__main__":
    import json

    user_question = "查询各大区的销售额"
    prompt = build_prompt(
        user_question,
        use_few_shot=True,
        use_rules=True,
        use_guards=True,
        use_include_join=True,
        use_schema_linking=True,
    )
    print(json.dumps(prompt, ensure_ascii=False, indent=2))
