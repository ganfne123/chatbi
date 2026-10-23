from security import UserContext
from typing import Any, Literal, Tuple
from pydantic import BaseModel,Field
from main import ChatBiSystem
from query_decomposer import DecompositionPlan,QureyAnalyse
from report_generat import ReportGenerat, Report

class PlanStep(BaseModel):
    step_id: str
    task_id: str
    step_name: str
    task_type: str
    question: str
    description: str
    depends_on: list[str] = Field(default_factory=list)
    depends_on_dec: str |None=None

    metrics: list[str] = Field(default_factory=list)
    # dimensions: list[str] = Field(default_factory=list)
    # expected_output: str


class StepExecutionResult(BaseModel):
    step_id: str
    task_id: str
    success: bool
    step_name: str
    task_type: str
    status: Literal["completed","failed","skipped"]="completed"
    attempts: int=1
    storage_backend: str | None=None
    result_reference: str | None=None
    question: str
    description: str
    sql: str =Field(default_factory=str)
    context_used: str = ""
    columns: list[str] = Field(default_factory=list)
    # rows: list[dict[str, Any]] = Field(default_factory=list)
    rows: list[tuple] =Field(default_factory=list)
    formatted: str = ""
    depends_on: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    error: str | None = None

class ExecutionSummary(BaseModel):
    """执行摘要。"""

    original_question: str
    analysis_goal: str
    completed_steps: int
    failed_steps: int
    skipped_steps: int = 0
    key_findings: list[str] = Field(default_factory=list)
    summary_text: str

class StepExecute:
    def __init__(self):
         self.memory_store=MemoryResultStore()
         self.chatbi=ChatBiSystem()
         self.retry_num=3


    def run(self,steps: list[PlanStep],user_context: UserContext) -> dict:
        # 已经执行过的步骤，用于组装依赖上下文
        visited_step: dict={}
        # 用于存储个步骤的主要信息

        for step in steps:
            if not self.check_depends(step.step_id,step.depends_on,visited_step):
                res = StepExecutionResult(
                    step_id=step.step_id,
                    task_id=step.task_id,
                    status="skipped",
                    success=False,
                    step_name=step.step_name,
                    attempts=0,
                    task_type=step.task_type,
                    question=step.question,
                    description=step.description,
                    depends_on=step.depends_on,
                    metrics=step.metrics,
                    error="依赖项被失败"
                )
                visited_step[step.step_id] = res
                self.memory_store.put(
                    step_id=step.step_id,
                    columns=visited_step[step.step_id].columns,
                    rows=visited_step[step.step_id].rows,
                )
                continue
            question = self._bulid_depends_prompt(
                step.question, step.depends_on, visited_step
            )
            sql_response,trynum = self.run_with_chatbi_retry(question,self.retry_num,user_context)

            if sql_response.get("success"):

                res = StepExecutionResult(
                    step_id=step.step_id,
                    task_id=step.task_id,
                    success=True,
                    status="completed",
                    step_name=step.step_name,
                    attempts=trynum,
                    task_type=step.task_type,
                    question=step.question,
                    description=step.description,
                    sql=sql_response["sql"],
                    columns=sql_response["columns"],
                    rows=sql_response["data"],
                    formatted=sql_response["formatted"],
                    depends_on=step.depends_on,
                    metrics=step.metrics,
                )  
            else:
                res = StepExecutionResult(
                    step_id=step.step_id,
                    task_id=step.task_id,
                    status="failed",
                    success=bool(sql_response.get("success", False)),
                    step_name=step.step_name,
                    attempts=trynum,
                    task_type=step.task_type,
                    question=step.question,
                    description=step.description,
                    depends_on=step.depends_on,
                    metrics=step.metrics,
                    error=str(sql_response.get("error", ""))
                )

            visited_step[step.step_id] = res
            self.memory_store.put(
                step_id=step.step_id,
                columns=visited_step[step.step_id].columns,
                rows=visited_step[step.step_id].rows,
            )
        return visited_step

    def _bulid_depends_prompt(self,query: str,depends_on: list , steps: dict) ->str:
        if not depends_on:
            return query
        for depend in depends_on:
            query+=f"{depend}数据描述为：{steps[depend].description}"
            query+=f"{depend}运行结果行为：{steps[depend].columns}"
            query+=f"{depend}运行结果列为：{steps[depend].rows}"
        return query


    def run_with_chatbi_retry(self, question: str, trynum: int, user_context: UserContext) -> Tuple[dict, int]:
        """执行一步；失败就把失败信息回喂给模型重试。

        :param trynum: 最多尝试次数（含首次），至少执行 1 次
        :return: (最后一次结果, 实际尝试次数)
        """
        max_attempts = max(1, trynum)
        attempts = 0
        last: dict | None = None
        seen: set[tuple] = set()
        while attempts < max_attempts:
            attempts += 1
            # 第一次不带 error_info；之后把上一轮结果（含失败的 sql 与报错）传回去
            last = self.chatbi.run(question, user_context, error_info=last if attempts > 1 else None)
            if last.get("success"):
                return last, attempts
            # 输入非法这类错误重试没有意义
            if last.get("error_type") == "validation":
                break
            # 模型这一轮没产出任何变化（SQL 与报错都一样），再重试只是白烧 token
            fingerprint = (last.get("sql") or "", last.get("error") or "")
            if fingerprint in seen:
                break
            seen.add(fingerprint)
        return last, attempts

    
    def check_depends(self,step_id: str,depend_on: list, steps: dict) ->bool:
        """检查依赖项是否完成"""
        for depend_id in depend_on:
            if steps[depend_id].status !="completed":
                return False
        return True
            





from query_decomposer import DecomposedTask
class PlanGenerate:
    def PlanGenerate(self,tasks: list[DecomposedTask]) ->list[PlanStep]:
        if not tasks:
            raise ValueError("llm规划不能为空")

        list_plan_step: list[PlanStep]=[]
        for index,task in enumerate(tasks,1):
            depends_on: list=[]
            for dep in task.depends_on:
                new_dep=dep.replace("task","step")
                depends_on.append(new_dep) 
                
            plan_step=PlanStep(
                step_id=f"step_{index}",
                task_id=task.task_id,
                step_name=task.task_name,
                task_type=task.task_type,
                question=self._build_step_question(task),
                depends_on=depends_on,
                metrics=task.metrics,
                # dimensions=task.dimensions,
                # expected_output="_build_expected_output(task)",
                description=task.description
            )
            list_plan_step.append(plan_step)
        return list_plan_step

    def _build_step_question(self,step: DecomposedTask) ->str:
        if  not step:
            raise ValueError("llm规划为空")
        query: str=""
        query+=step.description
        query+=("执行约束：本步骤只回答当前子任务，优先生成一条结构清晰、易执行的 SQL。/n")
        query+=("请优先返回支撑后续分析的查询结果，不要直接跳到最终归因结论。/n")
        return query






class MemoryResultStore:
    scheme = "memory"

    def __init__(self) -> None:
        self._store: dict = {}

    def put(self, step_id, columns, rows) -> str:
        reference = f"{self.scheme}://{step_id}"
        self._store[reference] = {"columns": list(columns), "rows": rows}
        return reference

    def get(self, reference) -> list[dict]:
        if reference not in self._store:
            raise KeyError(f"引用不存在：{reference}")
        return self._store[reference]
    def get_all(self) -> dict:
        """返回所有已存储的结果：{引用: {"columns": [...], "rows": [...]}}"""
        return dict(self._store)
    def get_all_values(self) -> list[dict]:
        """只返回数据本体，不含地址"""
        return list(self._store.values())

    def cleanup(self) -> None:
        self._store.clear()



class ResultSummarizer:
    def summarize(
            self,
            original_question: str,
            plan: DecompositionPlan,
            step_results: dict,
        ) -> ExecutionSummary:

        completed: list =[step for step in step_results.values() if step.status=="completed"]
        failed: list =[step for step in step_results.values() if step.status=="failed"]
        skipped: list =[step for step in step_results.values() if step.status=="skipped"]

        summary_text=f"""
完成的步骤数量{len(completed)}
失败的步骤数量{len(failed)}
跳过的步骤数量{len(skipped)}
"""     
        finding: str=""
        for step in step_results.values():
            if not step.formatted:
                finding+=f"描述：{step.question} 该步骤没有出现结果"
            else:
                finding+=f"描述：{step.question} 结果：{step.formatted}"

        return ExecutionSummary(
            original_question=original_question,
            analysis_goal=plan.analysis_goal,
            completed_steps=len(completed),
            failed_steps=len(failed),
            skipped_steps=len(skipped),
            key_findings=[finding],
            summary_text=summary_text
        )


# if __name__=="__main__":
#     query="前年利润怎么样"
#     agent=PlanAndExecuteAgnet()
#     agent.agnet_run(query)