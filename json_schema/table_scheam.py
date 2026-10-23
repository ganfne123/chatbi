# ==================== 表描述数据 ====================
# 每张表构建一段结构化的"自然语言描述"用于向量化检索
# 包含 5 张业务相关表 + 4 张不相关表，验证检索的区分能力
TABLE_METADATA = {
    # ---- 业务相关表 ----
    "dim_customers": {
        "description": (
            "客户维度表：存储客户基本信息，包括客户名称、客户类型"
            "（OEM整车厂、储能集成商、电网集团等）、所属行业（交通、能源、工业）、"
            "所在国家和销售大区（欧洲、北美、亚太等）。"
            "用于按客户维度分析收入、利润和订单分布。"
        ),
        "domain": "维度表",
        "key_fields": "customer_id, customer_name, customer_type, industry, country, region",
    },
    "dim_products": {
        "description": (
            "产品维度表：存储产品主数据，包括产品名称、产品线"
            "（动力电池-乘用车、储能系统-电网级等）、技术路线（三元锂、磷酸铁锂等）、"
            "以及产品成本信息（标准成本、材料成本、人工成本）。"
            "用于按产品维度分析收入、毛利、成本结构。"
        ),
        "domain": "维度表",
        "key_fields": "product_id, product_name, product_line, category, tech_route, standard_cost, material_cost, labor_cost",
    },
    "sales_orders": {
        "description": (
            "销售订单表：记录每笔销售订单的详细信息，包括订单日期、订单状态、"
            "数量、单价、折扣、含税总额（gross_amount）、不含税收入（net_amount）、币种。"
            "通过 customer_id 和 product_id 关联客户表和产品表。"
            "是收入分析、订单统计的核心事实表。"
        ),
        "domain": "事实表",
        "key_fields": "order_id, order_no, customer_id, product_id, region, order_date, order_status, quantity, unit_price, discount_amount, gross_amount, net_amount, currency",
    },
    "exchange_rates": {
        "description": (
            "汇率表：按日期和币种记录兑人民币汇率（rate_to_cny）。"
            "当订单涉及多币种时，需关联此表将金额统一折算为人民币。"
            "用于多币种收入汇总和跨区域财务对比。"
        ),
        "domain": "参考表",
        "key_fields": "rate_date, currency, rate_to_cny",
    },
    "finance_expenses": {
        "description": (
            "费用表：记录企业各部门的期间费用明细，包括研发费用、销售费用、"
            "管理费用、财务费用，以及销售费用的子项（市场费用、物流费用、质保费用）。"
            "用于费用分析、利润计算（利润 = 毛利 - 期间费用）。"
        ),
        "domain": "事实表",
        "key_fields": "expense_id, expense_date, department, rd_expense, selling_expense, admin_expense, finance_expense, marketing_expense, logistics_expense, warranty_expense",
    },
    # ---- 不相关表（用于验证检索区分能力）----
    "hr_attendance_records": {
        "description": (
            "人力考勤表：记录员工每日上下班打卡、请假、加班、排班班次和异常考勤。"
            "用于 HR 出勤统计、缺勤分析和薪资核算，不参与销售收入或产品利润分析。"
        ),
        "domain": "事实表",
        "key_fields": "record_id, employee_id, check_in_time, check_out_time, attendance_status, shift_type"
    },
    "iot_device_alerts": {
        "description": (
            "IoT 设备告警表：记录工厂设备、传感器、产线控制器上报的温度异常、"
            "震动异常、离线告警和维护工单。用于设备运维监控与预测性维护，"
            "不用于客户、订单、费用或汇率分析。"
        ),
        "domain": "事实表",
        "key_fields": "alert_id, device_id, alert_type, severity, alert_time, resolution_status"
    },
    "legal_contract_archive": {
        "description": (
            "法务合同档案表：存储合同编号、签署主体、法务审核意见、诉讼状态、"
            "保密条款和履约风险评级。用于合同管理与法务合规，不用于销售分析。"
        ),
        "domain": "维度表",
        "key_fields": "contract_id, contract_no, party_name, legal_opinion, litigation_status, risk_rating"
    },
    "warehouse_temperature_logs": {
        "description": (
            "仓储温湿度日志表：记录仓库各货位每小时温度、湿度、冷链设备状态和巡检结果。"
            "用于仓储环境监控和质量追溯，不用于收入、毛利、客户或费用统计。"
        ),
        "domain": "事实表",
        "key_fields": "log_id, warehouse_id, location_code, temperature, humidity, equipment_status"
    }
}