BUSINESS_RULES = [
    {
        "id": "rule_revenue",
        "name": "收入口径",
        "trigger_keywords": ["收入", "销售额", "营业收入", "营收", "销售收入", "净收入"],
        "force_include": ["sales_orders.net_amount"],
        "force_exclude": ["sales_orders.gross_amount"],
        "reason": "收入口径用 net_amount（不含税），排除 gross_amount（含税）",
    },
    {
        "id": "rule_tax_included",
        "name": "含税口径",
        "trigger_keywords": ["含税", "含税金额", "含税总额", "毛额", "税前"],
        "force_include": ["sales_orders.gross_amount"],
        "force_exclude": ["sales_orders.net_amount"],
        "reason": "含税口径用 gross_amount（含税），排除 net_amount（不含税）",
    },
]