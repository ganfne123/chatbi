# ==================== 表关联图配置 ====================
# 手动维护表间关系，原因：
# 1. 企业数据库常不建外键约束
# 2. 需要区分 JOIN / LEFT JOIN
# 3. 支持复合键
TABLE_RELATIONSHIPS = {
    # ---------- 事实表：销售订单 ----------
    "sales_orders": [
        {
            "target": "dim_customers",
            "fk_col": "customer_id",
            "pk_col": "customer_id",
            "join_type": "JOIN",
        },
        {
            "target": "dim_products",
            "fk_col": "product_id",
            "pk_col": "product_id",
            "join_type": "JOIN",
        },
        {
            "target": "dim_employees",
            "fk_col": "salesperson_id",
            "pk_col": "employee_id",
            "join_type": "LEFT JOIN",
        },
        {
            "target": "exchange_rates",
            "fk_col": "order_date, currency",
            "pk_col": "rate_date, currency",
            "join_type": "LEFT JOIN",
        },
    ],

    # ---------- 维度表：客户 ----------
    "dim_customers": [
        {
            "target": "sales_orders",
            "fk_col": "customer_id",
            "pk_col": "customer_id",
            "join_type": "LEFT JOIN",
        },
        {
            "target": "dim_employees",
            "fk_col": "account_manager_id",
            "pk_col": "employee_id",
            "join_type": "LEFT JOIN",
        },
    ],

    # ---------- 维度表：产品 ----------
    "dim_products": [
        {
            "target": "sales_orders",
            "fk_col": "product_id",
            "pk_col": "product_id",
            "join_type": "LEFT JOIN",
        },
    ],

    # ---------- 维度表：销售员（新增） ----------
    "dim_employees": [
        {
            "target": "sales_orders",
            "fk_col": "employee_id",
            "pk_col": "salesperson_id",
            "join_type": "LEFT JOIN",
        },
        {
            "target": "dim_customers",
            "fk_col": "employee_id",
            "pk_col": "account_manager_id",
            "join_type": "LEFT JOIN",
        },
    ],

    # ---------- 维度表：汇率 ----------
    "exchange_rates": [
        {
            "target": "sales_orders",
            "fk_col": "rate_date, currency",
            "pk_col": "order_date, currency",
            "join_type": "LEFT JOIN",
        },
    ],

    # 费用表与订单表在业务上独立，不建立直接关联
    "finance_expenses": [],
}