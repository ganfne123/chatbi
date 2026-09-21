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


class BuildPrompt:
    @staticmethod
    def build_prompt( query: str,schema : str = Schema)-> list:
        system= f"{SYSTEM_PROMPT} 数据库表的schema为：{schema}"
        user=f"用户问题为：{query}"
        message=[{"role":"system","content":system},{"role":"user","content":user}]
        return message        