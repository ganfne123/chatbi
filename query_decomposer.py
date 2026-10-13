"""query拆解器模块

将复杂的分析认为拆解成结构化的子任务
"""
from typing import Tuple
from jsonschema import ValidationError
from pydantic import BaseModel,Field

class DecomposedTask(BaseModel):

    task_id: str
    task_name: str
    task_type: str
    description: str
    depends_on: list[str] = Field(default_factory=list)
    # dimensions: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)

class DecompositionPlan(BaseModel):
    """复杂查询拆解结果。"""
    origin_query: str |None=None
    question_type: str
    analysis_goal: str
    subtasks: list[DecomposedTask]



from llm_client import LlmClient
from config import llm_config
class QureyAnalyse:
    def __init__(self):
        self.llm_client=LlmClient()
        self.llm_comfig=llm_config
        self.max_step=8


    def _format_schema_linking(self,schema_linking: dict | None) -> str:
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


    
    def _format_indicators(self,indicators: list[dict] | None) -> str:
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
    def build_prompt(self,query: str,
                    use_indicator: bool = False,
                    use_schema_linking: bool = False,
                    error: str |None=None
                    ) ->list:
        if not query:
            raise ValueError("用户问题不能为空")
        user_prompt=""
        if error is not None:
            user_prompt: str=error

        SYSTEM_PROMPT: str = """
        你是企业级 ChatBI 系统中的任务拆解器，
        用来对复杂的分析认为拆解成结构化的子任务，
        最后只能输出json
        """
        user_prompt+=f"""

        请将下面的复杂分析问题拆解为结构化子任务，并严格输出 JSON：

        用户问题：{query}

        输出要求：
        1. 顶层字段包含 question_type、analysis_goal、subtasks
        2. subtasks 是有序数组，每个任务必须包含：
        - task_id
        - task_name
        - task_type
        - description
        - depends_on
        - metrics
        3. task_id 使用 task_1、task_2 这类格式
        4. depends_on 只能引用前面已经出现的 task_id
        5. 每个子任务都应尽量对应一条简单 SQL 或一个单独分析动作，不要把多个分析都塞进同一步
        6. 仅返回 JSON 对象，不要使用 Markdown
        7. 指标优先复用【可用指标】中的名称或别名
        8. 只输出能被单条 SQL 回答的子任务；不要输出"结论汇总""报告归纳"之类的任务，归纳由下游报告模块完成。
        9. 如果一个任务同时要求多个维度或多个驱动因素，请拆成多个更简单的子任务，总任务数不的超过8个。
        10.只有当后一步必须用到前一步的计算结果数据时才填写 depends_on；若两步都能直接从明细表计算，则 depends_on 必须留空。

        【常见分析类型拆解策略】
        1. 趋势分析：优先拆成“主指标趋势 + 关键驱动项趋势 + 异常月份定位 + 原因归纳”，通常不超过 6 个子任务
        2. 原因诊断：优先拆成“结果趋势 + 构成拆解 + 关键维度定位 + 必要专项分析 + 结论汇总”，通常不超过 6 个子任务
        3. 维度对比：优先拆成“核心维度排名/贡献 + 必要补充维度 + 结论汇总”，通常不超过 5 个子任务
        """.strip()
        # 把 RAG 检索结果拼进 system prompt
        if use_schema_linking:
            from rag_retriever import run_schema_linking
            schema_text = self._format_schema_linking(run_schema_linking(query))
            if schema_text:
                user_prompt += f"以下是本系统能访问的数据范围。每个子任务必须能在这个范围内用一条 SQL 完成；不在范围内的分析角度不要拆。：\n{schema_text}\n"
        if use_indicator:
            from rag_retriever import run_indicator_search
            indicator_text = self._format_indicators(run_indicator_search(query))
            if indicator_text:
                user_prompt += f"以下是检索到的指标定义，计算口径请以此为准：\n{indicator_text}\n"
        
        prompt= [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
        return prompt

    def llm_generat(self,query: str,error: str | None=None) ->str:
        if not query:
            raise ValueError("用户问题不能为空")
        
        completion = self.llm_client.client.chat.completions.create(
            model=self.llm_comfig.get("model", "qwen3.7-plus"),
            messages=self.build_prompt(query,error=error),
            response_format={ "type": "json_object"},
            temperature=0,

        )
        content=completion.choices[0].message.content
        if content:
            return content
        else:
            raise ValueError("大模型返回为空")
    def parser_json(self,json: str) ->DecompositionPlan:
        if not json:
            raise ValueError("大模型生成为空")
        try:
            plan=DecompositionPlan.model_validate_json(json)
        except ValidationError as e:
                raise ValueError(f"拆解结果结构不合法: {e}")
        return plan


    def validata_plan(self,plan: DecompositionPlan) ->Tuple[bool,str]:
        visited=set()
        if len(plan.subtasks)>self.max_step:
            return False, "子任务的数量不的超过8个，请把多个指标或维度可以由同一条 SQL 的多个列同时产出，合并为一个子任务；不要按指标或按分析角度逐个拆分。"
        for subtasks in plan.subtasks:
            for depends_on in subtasks.depends_on:
                if depends_on == subtasks.task_id:
                    return False, f"{subtasks.task_id} 不能依赖自己"
                if depends_on not in visited:
                    return False, "depends_on出现了没有的taks_id"
            visited.add(subtasks.task_id)
        return True,""
    def run_retry(self,query: str, try_num: int= 3)-> DecompositionPlan:
        rwq_json=self.llm_generat(query)
        for currentCount in range(1,try_num+1):
            decompositionplan=self.parser_json(rwq_json)
            decompositionplan.origin_query=query
            success ,error=self.validata_plan(decompositionplan)
            if success:
                return decompositionplan
            else: 
                rwq_json=self.llm_generat(query,error)
                print(f"llm规划第{currentCount}次重试")
        raise EOFError
        
        

if __name__ == "__main__":
    client= QureyAnalyse()
    query="请全面分析公司2025年经营状况：收入、成本、费用、利润的趋势、结构、区域差异、产品线差异、异常点和改进建议"
    llm_plan = client.run_retry(query)
    print(llm_plan)




