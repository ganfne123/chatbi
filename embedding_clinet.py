
from dotenv import load_dotenv
load_dotenv()
import os
from openai import OpenAI
TABLE_DESCRIPTIONS = {
    # ============ 真实业务表 ============
    "dim_customers": (
        "客户维度表：存储客户基本信息，包括客户名称、客户类型"
        "（OEM 整车厂、储能集成商、电网集团等）、所属行业（交通、能源、工业）、"
        "所在国家和销售大区（欧洲、北美、亚太等）。"
        "用于按客户维度分析收入、利润和订单分布。"
    ),
    "dim_products": (
        "产品维度表：存储产品基本信息，包括产品名称、产品线、品类、"
        "技术路线（如磷酸铁锂、三元锂等），以及成本构成："
        "标准成本（standard_cost）、材料成本（material_cost）、人工成本（labor_cost）。"
        "用于产品结构分析、成本拆解和毛利测算。"
    ),
    "sales_orders": (
        "销售订单表：记录每笔销售订单的详细信息，包括订单日期、订单状态、"
        "数量、单价、折扣、含税总额（gross_amount）、不含税收入（net_amount）、币种。"
        "通过 customer_id 和 product_id 关联客户表和产品表。"
        "是收入分析、订单统计的核心事实表。"
    ),
    "finance_expenses": (
        "财务费用表：按部门和日期记录各项费用，包括研发费用（rd_expense）、"
        "销售费用（selling_expense）、管理费用（admin_expense）、财务费用（finance_expense）、"
        "市场费用（marketing_expense）、物流费用（logistics_expense）、质保费用（warranty_expense）。"
        "用于费用率分析、利润表编制和部门费用管控。"
    ),
    "exchange_rates": (
        "汇率表：记录各币种对人民币（CNY）的汇率，包括汇率日期（rate_date）、"
        "币种（currency）和汇率值（rate_to_cny）。"
        "用于将 sales_orders 中的多币种金额统一换算为人民币口径。"
    ),
    "dim_employees": (
        "员工维度表：存储员工基本信息，包括员工编号、姓名、部门、职位、"
        "入职日期、离职日期、薪资等级。"
        "用于人力资源分析，与销售、财务分析无直接关联。"
    ),
    "hr_attendance": (
        "考勤记录表：记录员工每日打卡信息，包括员工编号、打卡日期、"
        "上班时间、下班时间、迟到分钟数、加班时长。"
        "用于考勤统计，与销售订单、财务费用分析无关。"
    ),
    "it_assets": (
        "IT 资产表：记录公司 IT 设备信息，包括资产编号、设备类型、"
        "品牌型号、采购日期、保修到期日、使用人、所在机房。"
        "用于 IT 资产管理，与业务经营分析无关。"
    ),
    "office_supplies": (
        "办公用品表：记录办公用品采购与领用信息，包括物品编号、名称、"
        "类别、采购数量、领用部门、领用人、领用日期。"
        "用于行政后勤管理，与销售和财务分析无关。"
    ),
    "website_logs": (
        "网站访问日志表：记录官网访问日志，包括访问时间、访客 IP、"
        "访问页面、停留时长、来源渠道、设备类型。"
        "用于网站流量分析，与订单、客户、财务数据无关联。"
    ),
    "weather_data": (
        "天气数据表：记录各城市每日天气，包括日期、城市、温度、"
        "湿度、降水量、风向、风力等级。"
        "用于外部环境分析，与公司经营数据无直接关联。"
    ),

}
class EmbeddingClient:
    # 关键：将 base_url 替换为你实际使用的服务商地址
    # 如果你用的是阿里云百炼（国内），通常是：
    def __init__(self):
        
        self.client = OpenAI(
            api_key=os.getenv("EMBEDDING_TOKEN",""), 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1" 
        )

    # 关键：调用正确的模型名称
    def get_embedding(self,text: str) ->list[float]:
        resp =self.client.embeddings.create(
            model=os.getenv("EMBEDDING_MODEL_NAME",""),
            input=text,
        )
        return resp.data[0].embedding

    def build_table_index(self,table: dict = TABLE_DESCRIPTIONS) -> dict[str, list[float]]:
        """将所有表的描述文本转为 Embedding 向量，构建内存索引"""
        index={}
        for name,chunk in table.items():
            vector=self.get_embedding(chunk)
            index[name]=vector
        return index

# if __name__=="__main__":
#     client=EmbeddingClient()
#     resp=client.get_embedding("中国")
#     print(resp)