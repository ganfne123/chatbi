FIELD_METADATA = {
    # ---- dim_customers ----
    "dim_customers.customer_id": {
        "table": "dim_customers",
        "field": "customer_id",
        "description": (
            "客户唯一标识（主键），INT 类型。"
            "用于关联 sales_orders 表的外键 customer_id。"
        ),
        "domain": "维度表",
    },
    "dim_customers.customer_name": {
        "table": "dim_customers",
        "field": "customer_name",
        "description": (
            "客户名称，VARCHAR(100)。"
            "示例：宝马集团、国家电网、特斯拉。"
            "用于查询特定客户的订单或收入。"
        ),
        "domain": "维度表",
    },
    "dim_customers.customer_type": {
        "table": "dim_customers",
        "field": "customer_type",
        "description": (
            "客户类型分类，VARCHAR(50)。"
            "枚举值：OEM整车厂 / 储能集成商 / 电网集团 / 工商业用户 / 换电运营商 / 经销商。"
            "用于按客户类型维度做收入、订单分布分析。"
        ),
        "domain": "维度表",
    },
    "dim_customers.industry": {
        "table": "dim_customers",
        "field": "industry",
        "description": (
            "客户所属行业，VARCHAR(50)。"
            "枚举值：交通 / 能源 / 工业 / 特种交通。"
            "用于按行业维度统计客户分布和收入占比。"
        ),
        "domain": "维度表",
    },
    "dim_customers.country": {
        "table": "dim_customers",
        "field": "country",
        "description": (
            "客户所在的具体国家，VARCHAR(50)。"
            "示例：Germany、United States、Japan、China。"
            "注意与 region（大区）的区别：country 是具体国家，region 是地区分组。"
            "当问题提到具体国家名称时使用此字段。"
        ),
        "domain": "维度表",
    },
    "dim_customers.region": {
        "table": "dim_customers",
        "field": "region",
        "description": (
            "客户所属的销售大区，VARCHAR(50)。"
            "枚举值：欧洲 / 北美 / 亚太 / 中东非洲 / 拉美。"
            "注意与 country（国家）的区别：region 是大区汇总维度。"
            "当问题说'某个市场/大区'时使用此字段，说具体国家名时用 country。"
        ),
        "domain": "维度表",
    },
    # ---- dim_products ----
    "dim_products.product_id": {
        "table": "dim_products",
        "field": "product_id",
        "description": (
            "产品唯一标识（主键），INT 类型。"
            "用于关联 sales_orders 表的外键 product_id。"
        ),
        "domain": "维度表",
    },
    "dim_products.product_name": {
        "table": "dim_products",
        "field": "product_name",
        "description": (
            "产品名称，VARCHAR(100)。"
            "示例：极氪001专用电池包、电网级液冷储能柜。"
            "用于查询特定产品的销量或收入。"
        ),
        "domain": "维度表",
    },
    "dim_products.product_line": {
        "table": "dim_products",
        "field": "product_line",
        "description": (
            "产品线分类，VARCHAR(50)。"
            "枚举值：动力电池-乘用车 / 动力电池-商用车 / 储能系统-电网级 / "
            "储能系统-工商业 / 电池材料与回收。"
            "用于按产品线维度分析收入、毛利。"
            "当用户提到'各产品线'或'按业务板块'时使用此字段。"
        ),
        "domain": "维度表",
    },
    "dim_products.category": {
        "table": "dim_products",
        "field": "category",
        "description": (
            "产品分类（细分品类），VARCHAR(50)。"
            "枚举值：高能量密度型 / 超快充型 / 混动专用型 / 低温适配型 / "
            "商用车标准型 / 电网级储能型 / 工商业储能型。"
            "比 product_line 更细的产品分类维度。"
        ),
        "domain": "维度表",
    },
    "dim_products.tech_route": {
        "table": "dim_products",
        "field": "tech_route",
        "description": (
            "技术路线，VARCHAR(50)。"
            "枚举值：三元锂 / 磷酸铁锂 / 钠离子 / 固态电池。"
            "用于按技术路线分析产品结构和成本差异。"
        ),
        "domain": "维度表",
    },
    "dim_products.standard_cost": {
        "table": "dim_products",
        "field": "standard_cost",
        "description": (
            "产品标准成本，DECIMAL(10,2)。"
            "= material_cost + labor_cost + 制造费用分摊。"
            "用于核算产品总成本。注意：毛利计算建议用 material_cost + labor_cost。"
        ),
        "domain": "维度表",
    },
    "dim_products.material_cost": {
        "table": "dim_products",
        "field": "material_cost",
        "description": (
            "材料成本，DECIMAL(10,2)。"
            "产品的原材料采购成本（正极材料、电解液、隔膜等）。"
            "毛利计算公式中的核心组成部分：毛利 = net_amount - (material_cost + labor_cost) * quantity。"
        ),
        "domain": "维度表",
    },
    "dim_products.labor_cost": {
        "table": "dim_products",
        "field": "labor_cost",
        "description": (
            "人工成本，DECIMAL(10,2)。"
            "产品的人工制造成本。"
            "毛利计算公式中的核心组成部分：毛利 = net_amount - (material_cost + labor_cost) * quantity。"
        ),
        "domain": "维度表",
    },
    # ---- sales_orders ----
    "sales_orders.order_id": {
        "table": "sales_orders",
        "field": "order_id",
        "description": "订单唯一标识（主键），BIGINT 类型。",
        "domain": "事实表",
    },
    "sales_orders.order_no": {
        "table": "sales_orders",
        "field": "order_no",
        "description": (
            "订单编号，VARCHAR(50)。业务编号，格式如 ORD-2026-001234。"
            "用于查询特定订单明细。"
        ),
        "domain": "事实表",
    },
    "sales_orders.customer_id": {
        "table": "sales_orders",
        "field": "customer_id",
        "description": (
            "客户外键，INT。关联 dim_customers.customer_id。"
            "当需要按客户维度分析时，通过此字段 JOIN dim_customers。"
        ),
        "domain": "事实表",
    },
    "sales_orders.product_id": {
        "table": "sales_orders",
        "field": "product_id",
        "description": (
            "产品外键，INT。关联 dim_products.product_id。"
            "当需要按产品维度分析时，通过此字段 JOIN dim_products。"
        ),
        "domain": "事实表",
    },
    "sales_orders.region": {
        "table": "sales_orders",
        "field": "region",
        "description": (
            "订单销售区域（冗余字段），VARCHAR(50)。"
            "枚举值：欧洲 / 北美 / 亚太 / 中东非洲 / 拉美。"
            "与 dim_customers.region 相同，冗余存储在订单表中便于直接筛选。"
            "当只需按大区过滤收入且不需要其他客户信息时，可直接使用此字段避免 JOIN。"
        ),
        "domain": "事实表",
    },
    "sales_orders.order_date": {
        "table": "sales_orders",
        "field": "order_date",
        "description": (
            "订单日期，DATE 类型。格式 YYYY-MM-DD。"
            "所有时间范围筛选（本月、上月、最近N个月、季度、年度）都基于此字段。"
            "也用于关联 exchange_rates.rate_date 进行汇率换算。"
        ),
        "domain": "事实表",
    },
    "sales_orders.order_status": {
        "table": "sales_orders",
        "field": "order_status",
        "description": (
            "订单状态，VARCHAR(20)。"
            "枚举值：completed（已完成）/ cancelled（已取消）/ pending（待处理）。"
            "统计收入、订单量等指标时，必须过滤 order_status = 'completed'。"
        ),
        "domain": "事实表",
    },
    "sales_orders.quantity": {
        "table": "sales_orders",
        "field": "quantity",
        "description": (
            "订单数量，DECIMAL(10,2)。单位为 MWh 或套数。"
            "用于统计销量、计算成本（cost * quantity）。"
        ),
        "domain": "事实表",
    },
    "sales_orders.unit_price": {
        "table": "sales_orders",
        "field": "unit_price",
        "description": (
            "单价（不含税），DECIMAL(10,2)。每 MWh 或每套的价格。"
            "用于分析定价策略、计算客单价。"
        ),
        "domain": "事实表",
    },
    "sales_orders.discount_amount": {
        "table": "sales_orders",
        "field": "discount_amount",
        "description": (
            "折扣金额，DECIMAL(10,2)。该订单的折扣优惠金额。"
            "用于分析折扣力度、计算实际售价。"
        ),
        "domain": "事实表",
    },
    "sales_orders.gross_amount": {
        "table": "sales_orders",
        "field": "gross_amount",
        "description": (
            "含税总额，DECIMAL(12,2)。包含增值税的订单总金额。"
            "注意：除非用户明确要求'含税金额'，否则不应使用此字段。"
            "日常说的'收入''销售额'统一使用 net_amount（不含税收入）。"
        ),
        "domain": "事实表",
    },
    "sales_orders.net_amount": {
        "table": "sales_orders",
        "field": "net_amount",
        "description": (
            "不含税收入（财务口径的销售额），DECIMAL(12,2)。"
            "这是业务中'收入''销售额''营业收入'的标准字段。"
            "毛利计算：毛利 = net_amount - (material_cost + labor_cost) * quantity。"
            "统计收入时必须同时过滤 order_status = 'completed'。"
        ),
        "domain": "事实表",
    },
    "sales_orders.currency": {
        "table": "sales_orders",
        "field": "currency",
        "description": (
            "订单币种，VARCHAR(10)。示例：CNY、USD、EUR、JPY。"
            "当涉及多币种收入汇总时，需通过 currency + order_date 关联 exchange_rates 表。"
        ),
        "domain": "事实表",
    },
    # ---- exchange_rates ----
    "exchange_rates.rate_date": {
        "table": "exchange_rates",
        "field": "rate_date",
        "description": (
            "汇率日期，DATE 类型。"
            "通过 sales_orders.order_date = exchange_rates.rate_date 关联。"
        ),
        "domain": "参考表",
    },
    "exchange_rates.currency": {
        "table": "exchange_rates",
        "field": "currency",
        "description": (
            "币种代码，VARCHAR(10)。示例：USD、EUR、JPY。"
            "通过 sales_orders.currency = exchange_rates.currency 关联。"
        ),
        "domain": "参考表",
    },
    "exchange_rates.rate_to_cny": {
        "table": "exchange_rates",
        "field": "rate_to_cny",
        "description": (
            "兑人民币汇率，DECIMAL(10,4)。"
            "换算公式：人民币金额 = 外币金额 * rate_to_cny。"
            "用于多币种收入统一折算为人民币。"
        ),
        "domain": "参考表",
    },
    # ---- finance_expenses ----
    "finance_expenses.expense_id": {
        "table": "finance_expenses",
        "field": "expense_id",
        "description": "费用记录唯一标识（主键），BIGINT 类型。",
        "domain": "事实表",
    },
    "finance_expenses.expense_date": {
        "table": "finance_expenses",
        "field": "expense_date",
        "description": (
            "费用日期，DATE 类型。格式 YYYY-MM-DD。"
            "用于按时间段筛选费用记录。"
        ),
        "domain": "事实表",
    },
    "finance_expenses.department": {
        "table": "finance_expenses",
        "field": "department",
        "description": (
            "部门名称，VARCHAR(50)。"
            "示例：研发部、销售部、管理部。"
            "用于按部门维度分析费用。"
        ),
        "domain": "事实表",
    },
    "finance_expenses.rd_expense": {
        "table": "finance_expenses",
        "field": "rd_expense",
        "description": (
            "研发费用，DECIMAL(12,2)。"
            "企业研发投入（电池技术研发、储能系统研发等）。"
            "新能源企业研发投入占比高，是重要的费用分析维度。"
        ),
        "domain": "事实表",
    },
    "finance_expenses.selling_expense": {
        "table": "finance_expenses",
        "field": "selling_expense",
        "description": (
            "销售费用（总项），DECIMAL(12,2)。"
            "包含子项：marketing_expense + logistics_expense + warranty_expense。"
            "注意：汇总时不要重复计算！selling_expense 已包含其子项。"
        ),
        "domain": "事实表",
    },
    "finance_expenses.admin_expense": {
        "table": "finance_expenses",
        "field": "admin_expense",
        "description": (
            "管理费用，DECIMAL(12,2)。"
            "行政管理相关费用。"
        ),
        "domain": "事实表",
    },
    "finance_expenses.finance_expense": {
        "table": "finance_expenses",
        "field": "finance_expense",
        "description": (
            "财务费用，DECIMAL(12,2)。"
            "利息支出、汇兑损益等财务相关费用。"
        ),
        "domain": "事实表",
    },
    "finance_expenses.marketing_expense": {
        "table": "finance_expenses",
        "field": "marketing_expense",
        "description": (
            "市场费用，DECIMAL(12,2)。"
            "属于 selling_expense 的子项。包括展会、广告、品牌推广等。"
            "注意：是销售费用的子项，不可与 selling_expense 加总。"
        ),
        "domain": "事实表",
    },
    "finance_expenses.logistics_expense": {
        "table": "finance_expenses",
        "field": "logistics_expense",
        "description": (
            "物流费用，DECIMAL(12,2)。"
            "属于 selling_expense 的子项。电池产品运输、仓储等费用。"
            "注意：是销售费用的子项，不可与 selling_expense 加总。"
        ),
        "domain": "事实表",
    },
    "finance_expenses.warranty_expense": {
        "table": "finance_expenses",
        "field": "warranty_expense",
        "description": (
            "质保费用，DECIMAL(12,2)。"
            "属于 selling_expense 的子项。电池质保期内的维修、更换费用。"
            "注意：是销售费用的子项，不可与 selling_expense 加总。"
        ),
        "domain": "事实表",
    },
        # ---- dim_employees ----
    "dim_employees.employee_id": {
        "table": "dim_employees",
        "field": "employee_id",
        "description": (
            "员工唯一标识（主键），INT 类型。"
            "用于关联 hr_attendance 表的外键 employee_id。"
        ),
        "domain": "维度表（人力资源）",
    },
    "dim_employees.employee_name": {
        "table": "dim_employees",
        "field": "employee_name",
        "description": (
            "员工姓名，VARCHAR(50)。"
            "用于 HR 查询、考勤统计。"
            "与客户无关：员工是公司内部人员，不是外部客户。"
        ),
        "domain": "维度表（人力资源）",
    },
    "dim_employees.department": {
        "table": "dim_employees",
        "field": "department",
        "description": (
            "员工所属部门，VARCHAR(50)。"
            "示例：研发部、销售部、管理部。"
            "注意与 finance_expenses.department 区别：此字段是员工组织归属，"
            "finance_expenses.department 是费用归属部门，两者可能同名但语义不同。"
        ),
        "domain": "维度表（人力资源）",
    },
    "dim_employees.position": {
        "table": "dim_employees",
        "field": "position",
        "description": (
            "员工职位，VARCHAR(50)。"
            "示例：工程师、经理、总监。"
            "与 salary_level 区别：position 是岗位，salary_level 是薪酬级别。"
        ),
        "domain": "维度表（人力资源）",
    },
    "dim_employees.hire_date": {
        "table": "dim_employees",
        "field": "hire_date",
        "description": (
            "入职日期，DATE 类型。"
            "用于计算司龄、入职趋势分析。"
            "与 leave_date 区别：hire_date 是入职，leave_date 是离职。"
        ),
        "domain": "维度表（人力资源）",
    },
    "dim_employees.leave_date": {
        "table": "dim_employees",
        "field": "leave_date",
        "description": (
            "离职日期，DATE 类型。在职员工为 NULL。"
            "用于在职状态判断、离职率分析。"
            "与 hire_date 区别：本字段是离职日期。"
        ),
        "domain": "维度表（人力资源）",
    },
    "dim_employees.salary_level": {
        "table": "dim_employees",
        "field": "salary_level",
        "description": (
            "薪资等级，VARCHAR(20)。"
            "示例：P5、P6、P7。"
            "用于薪酬结构分析。"
            "与 position 区别：salary_level 是薪酬级别，position 是岗位名称。"
        ),
        "domain": "维度表（人力资源）",
    },

    # ---- hr_attendance ----
    "hr_attendance.attendance_id": {
        "table": "hr_attendance",
        "field": "attendance_id",
        "description": "考勤记录唯一标识（主键），BIGINT 类型。",
        "domain": "事实表（人力资源）",
    },
    "hr_attendance.employee_id": {
        "table": "hr_attendance",
        "field": "employee_id",
        "description": (
            "员工外键，INT 类型。关联 dim_employees.employee_id。"
            "与 customer_id 区别：员工是内部人员，客户是外部实体。"
        ),
        "domain": "事实表（人力资源）",
    },
    "hr_attendance.attendance_date": {
        "table": "hr_attendance",
        "field": "attendance_date",
        "description": (
            "打卡日期，DATE 类型。"
            "用于按日/月统计考勤。"
            "与 order_date 区别：考勤日期与销售业务无关。"
        ),
        "domain": "事实表（人力资源）",
    },
    "hr_attendance.check_in_time": {
        "table": "hr_attendance",
        "field": "check_in_time",
        "description": (
            "上班打卡时间，TIME 类型。"
            "用于迟到判断。"
            "与 check_out_time 区别：check_in_time 是上班，check_out_time 是下班。"
        ),
        "domain": "事实表（人力资源）",
    },
    "hr_attendance.check_out_time": {
        "table": "hr_attendance",
        "field": "check_out_time",
        "description": (
            "下班打卡时间，TIME 类型。"
            "用于加班判断。"
            "与 check_in_time 区别：本字段是下班打卡。"
        ),
        "domain": "事实表（人力资源）",
    },
    "hr_attendance.late_minutes": {
        "table": "hr_attendance",
        "field": "late_minutes",
        "description": (
            "迟到分钟数，INT 类型。"
            "用于迟到统计。"
            "与 overtime_hours 区别：late_minutes 是迟到，overtime_hours 是加班。"
        ),
        "domain": "事实表（人力资源）",
    },
    "hr_attendance.overtime_hours": {
        "table": "hr_attendance",
        "field": "overtime_hours",
        "description": (
            "加班时长（小时），DECIMAL(5,2)。"
            "用于加班统计。"
            "与 late_minutes 区别：本字段是加班时长。"
        ),
        "domain": "事实表（人力资源）",
    },

    # ---- it_assets ----
    "it_assets.asset_id": {
        "table": "it_assets",
        "field": "asset_id",
        "description": "资产编号（主键），INT 类型。",
        "domain": "维度表（IT与行政）",
    },
    "it_assets.asset_type": {
        "table": "it_assets",
        "field": "asset_type",
        "description": (
            "资产类型，VARCHAR(50)。"
            "示例：笔记本电脑、服务器、路由器。"
            "与 product_id 区别：IT 资产是内部设备，不是销售产品。"
        ),
        "domain": "维度表（IT与行政）",
    },
    "it_assets.brand_model": {
        "table": "it_assets",
        "field": "brand_model",
        "description": (
            "品牌型号，VARCHAR(100)。"
            "用于资产识别。"
            "与 product_name 区别：brand_model 是 IT 设备型号，不是销售产品。"
        ),
        "domain": "维度表（IT与行政）",
    },
    "it_assets.purchase_date": {
        "table": "it_assets",
        "field": "purchase_date",
        "description": (
            "采购日期，DATE 类型。"
            "用于资产折旧计算。"
            "与 order_date 区别：purchase_date 是内部采购，不是销售订单日期。"
        ),
        "domain": "维度表（IT与行政）",
    },
    "it_assets.warranty_end_date": {
        "table": "it_assets",
        "field": "warranty_end_date",
        "description": (
            "保修到期日期，DATE 类型。"
            "用于保修状态判断。"
            "与 purchase_date 区别：本字段是保修截止日。"
        ),
        "domain": "维度表（IT与行政）",
    },
    "it_assets.user_name": {
        "table": "it_assets",
        "field": "user_name",
        "description": (
            "使用人姓名，VARCHAR(50)。"
            "用于资产归属查询。"
            "与 employee_name 区别：user_name 是资产使用人，可能非本公司员工。"
        ),
        "domain": "维度表（IT与行政）",
    },
    "it_assets.location": {
        "table": "it_assets",
        "field": "location",
        "description": (
            "所在机房/物理位置，VARCHAR(100)。"
            "用于资产位置管理。"
            "与 region 区别：location 是物理位置，region 是销售大区。"
        ),
        "domain": "维度表（IT与行政）",
    },

    # ---- office_supplies ----
    "office_supplies.supply_id": {
        "table": "office_supplies",
        "field": "supply_id",
        "description": "办公用品编号（主键），INT 类型。",
        "domain": "事实表（IT与行政）",
    },
    "office_supplies.supply_name": {
        "table": "office_supplies",
        "field": "supply_name",
        "description": (
            "办公用品名称，VARCHAR(100)。"
            "示例：打印纸、签字笔、文件夹。"
            "与 product_name 区别：办公用品是内部消耗品，不是销售产品。"
        ),
        "domain": "事实表（IT与行政）",
    },
    "office_supplies.category": {
        "table": "office_supplies",
        "field": "category",
        "description": (
            "办公用品类别，VARCHAR(50)。"
            "示例：纸张、文具、耗材。"
            "与 dim_products.category 区别：本字段是办公用品类别，不是产品品类。"
        ),
        "domain": "事实表（IT与行政）",
    },
    "office_supplies.purchase_quantity": {
        "table": "office_supplies",
        "field": "purchase_quantity",
        "description": (
            "采购数量，INT 类型。"
            "用于采购统计。"
            "与 sales_orders.quantity 区别：本字段是内部采购数量。"
        ),
        "domain": "事实表（IT与行政）",
    },
    "office_supplies.department": {
        "table": "office_supplies",
        "field": "department",
        "description": (
            "领用部门，VARCHAR(50)。"
            "用于部门办公用品成本分析。"
            "与 finance_expenses.department 区别：本字段是领用部门，"
            "finance_expenses.department 是费用归属部门。"
        ),
        "domain": "事实表（IT与行政）",
    },
    "office_supplies.recipient": {
        "table": "office_supplies",
        "field": "recipient",
        "description": (
            "领用人姓名，VARCHAR(50)。"
            "用于领用记录追踪。"
            "与 employee_name 区别：recipient 是办公用品领用人。"
        ),
        "domain": "事实表（IT与行政）",
    },
    "office_supplies.issue_date": {
        "table": "office_supplies",
        "field": "issue_date",
        "description": (
            "领用日期，DATE 类型。"
            "用于领用时间分析。"
            "与 order_date 区别：issue_date 是办公用品领用日期。"
        ),
        "domain": "事实表（IT与行政）",
    },

    # ---- website_logs ----
    "website_logs.log_id": {
        "table": "website_logs",
        "field": "log_id",
        "description": "日志唯一标识（主键），BIGINT 类型。",
        "domain": "事实表（网站与外部数据）",
    },
    "website_logs.visit_time": {
        "table": "website_logs",
        "field": "visit_time",
        "description": (
            "访问时间，DATETIME 类型。"
            "用于流量时间分析。"
            "与 order_date 区别：visit_time 是网站访问时间。"
        ),
        "domain": "事实表（网站与外部数据）",
    },
    "website_logs.visitor_ip": {
        "table": "website_logs",
        "field": "visitor_ip",
        "description": (
            "访客 IP 地址，VARCHAR(45)。"
            "用于访客识别、地域分析。"
            "与 customer_id 区别：IP 是匿名访客，不是客户实体。"
        ),
        "domain": "事实表（网站与外部数据）",
    },
    "website_logs.page_url": {
        "table": "website_logs",
        "field": "page_url",
        "description": (
            "访问页面 URL，VARCHAR(255)。"
            "用于页面热度分析。"
            "与 product_name 区别：page_url 是网页地址。"
        ),
        "domain": "事实表（网站与外部数据）",
    },
    "website_logs.stay_duration": {
        "table": "website_logs",
        "field": "stay_duration",
        "description": (
            "停留时长（秒），INT 类型。"
            "用于用户行为分析。"
            "与 overtime_hours 区别：stay_duration 是网页停留时长。"
        ),
        "domain": "事实表（网站与外部数据）",
    },
    "website_logs.source_channel": {
        "table": "website_logs",
        "field": "source_channel",
        "description": (
            "来源渠道，VARCHAR(50)。"
            "示例：百度、谷歌、直接访问。"
            "与 dim_customers.customer_type 区别：source_channel 是流量来源渠道。"
        ),
        "domain": "事实表（网站与外部数据）",
    },
    "website_logs.device_type": {
        "table": "website_logs",
        "field": "device_type",
        "description": (
            "设备类型，VARCHAR(20)。"
            "示例：PC、Mobile、Tablet。"
            "与 it_assets.asset_type 区别：device_type 是访客设备类型。"
        ),
        "domain": "事实表（网站与外部数据）",
    },

    # ---- weather_data ----
    "weather_data.weather_id": {
        "table": "weather_data",
        "field": "weather_id",
        "description": "天气记录唯一标识（主键），BIGINT 类型。",
        "domain": "参考表（网站与外部数据）",
    },
    "weather_data.weather_date": {
        "table": "weather_data",
        "field": "weather_date",
        "description": (
            "天气日期，DATE 类型。"
            "用于天气时间分析。"
            "与 order_date 区别：weather_date 是天气日期。"
        ),
        "domain": "参考表（网站与外部数据）",
    },
    "weather_data.city": {
        "table": "weather_data",
        "field": "city",
        "description": (
            "城市名称，VARCHAR(50)。"
            "用于城市天气查询。"
            "与 dim_customers.country 区别：city 是城市，country 是国家。"
        ),
        "domain": "参考表（网站与外部数据）",
    },
    "weather_data.temperature": {
        "table": "weather_data",
        "field": "temperature",
        "description": (
            "温度（摄氏度），DECIMAL(5,2)。"
            "用于天气分析。"
            "与 sales_orders.quantity 区别：temperature 是温度值。"
        ),
        "domain": "参考表（网站与外部数据）",
    },
    "weather_data.humidity": {
        "table": "weather_data",
        "field": "humidity",
        "description": (
            "湿度（百分比），DECIMAL(5,2)。"
            "用于天气分析。"
            "与 temperature 区别：humidity 是湿度。"
        ),
        "domain": "参考表（网站与外部数据）",
    },
    "weather_data.precipitation": {
        "table": "weather_data",
        "field": "precipitation",
        "description": (
            "降水量（mm），DECIMAL(5,2)。"
            "用于天气分析。"
            "与 humidity 区别：precipitation 是降水量。"
        ),
        "domain": "参考表（网站与外部数据）",
    },
    "weather_data.wind_direction": {
        "table": "weather_data",
        "field": "wind_direction",
        "description": (
            "风向，VARCHAR(20)。"
            "示例：北风、东南风。"
            "与 wind_level 区别：wind_direction 是风向。"
        ),
        "domain": "参考表（网站与外部数据）",
    },
    "weather_data.wind_level": {
        "table": "weather_data",
        "field": "wind_level",
        "description": (
            "风力等级，INT 类型。"
            "示例：3、5。"
            "与 wind_direction 区别：wind_level 是风力等级。"
        ),
        "domain": "参考表（网站与外部数据）",
    },
}

