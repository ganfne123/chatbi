# ==================== 业务规则层 ====================
# 规则类型：whitelist（强制包含）、blacklist（强制排除）、conditional（条件触发）
BUSINESS_RULES = [
    # --- 收入口径规则 ---
    {
        "type": "whitelist",
        "trigger_keywords": ["收入", "销售额", "营业收入", "营收"],
        "force_include": ["sales_orders.net_amount"],
        "reason": "收入口径统一使用 net_amount（不含税）",
    },
    {
        "type": "blacklist",
        "trigger_keywords": ["收入", "销售额", "营业收入", "营收"],
        "force_exclude": ["sales_orders.gross_amount"],
        "reason": "除非明确要求含税，否则排除 gross_amount",
    },
    # --- 含税场景例外 ---
    {
        "type": "whitelist",
        "trigger_keywords": ["含税", "含税金额", "含税收入"],
        "force_include": ["sales_orders.gross_amount"],
        "reason": "用户明确要求含税时使用 gross_amount",
    },
    {
        "type": "blacklist",
        "trigger_keywords": ["含税", "含税金额", "含税收入"],
        "force_exclude": ["sales_orders.net_amount"],
        "reason": "用户明确要求含税时禁用 net_amount",
    },
    # --- 成本口径规则 ---
    {
        "type": "whitelist",
        "trigger_keywords": ["成本", "毛利", "利润"],
        "force_include": ["dim_products.material_cost", "dim_products.labor_cost"],
        "reason": "成本计算使用 material_cost + labor_cost",
    },
    # --- 订单过滤规则 ---
    {
        "type": "whitelist",
        "trigger_keywords": ["收入", "销售额", "订单量", "订单数", "客单价"],
        "force_include": ["sales_orders.order_status"],
        "reason": "收入类统计必须包含 order_status 用于过滤 completed",
    },
    # --- 费用层级保护 ---
    {
        "type": "blacklist",
        "trigger_keywords": ["总费用", "期间费用合计", "费用汇总"],
        "force_exclude": [
            "finance_expenses.marketing_expense",
            "finance_expenses.logistics_expense",
            "finance_expenses.warranty_expense",
        ],
        "reason": "汇总费用时排除子项字段，避免重复计算",
    },
]