"""报告生成模块：定义 LLM 分析报告的结构化契约。

字段按来源分两类：

- 程序填充：question / raw_content / parse_error
- LLM 填充：conclusion / insights / recommendations

解析失败时叙述层留空并记录 parse_error，原始输出保留在 raw_content。
"""
import json
import re
from typing import TYPE_CHECKING, Tuple

from openai import OpenAIError
from pydantic import BaseModel, Field

from llm_client import LlmClient

if TYPE_CHECKING:  # 仅用于类型注解，避免与 agnet_planner 形成循环导入
    from agnet_planner import ExecutionSummary


SYSTEM_PROMPT = """你是企业 ChatBI 系统的分析报告撰写者。你会读到若干已执行完毕的分析步骤结果，
需要归纳出结论，直接回答用户的问题。

要求：
1. 只依据给定数据作答，不得编造任何数字或未出现的事实；
2. conclusion 要给出归因判断，不要复述用户问题；
3. insights 按重要性排序，每条一句话且必须包含关键数字；
4. recommendations 给出 2~4 条可执行建议，每条一句话；
5. 若有步骤失败或被跳过，需在结论中说明结论的局限；
6. 全部使用中文纯文本，不要 Markdown 语法；
7. 只输出一个 JSON 对象，不要输出解释文字，也不要用 ``` 代码块包裹。

输出字段：
- conclusion: 字符串，总体结论，直接回答用户问题
- insights: 字符串数组，支撑结论的要点，每条一句话
- recommendations: 字符串数组，可执行建议，2~4 条

注意：question、raw_content、parse_error 由程序填充，你不要输出这些字段。"""


class Report(BaseModel):
    """分析报告的最终产物。"""

    # --- 元信息（程序填充）---
    question: str = Field(default="", description="用户的原始问题，由程序回填。")


    # --- 叙述层（LLM 填充）---
    conclusion: str = Field(default="", description="总体结论，直接回答用户问题。")
    insights: list[str] = Field(default_factory=list, description="支撑结论的要点，每条一句话，纯文本。")
    recommendations: list[str] = Field(default_factory=list, description="可执行建议，2~4 条。")

    # --- 兜底 ---
    raw_content: str | None = Field(default=None, description="模型返回的原始文本。")
    parse_error: str | None = Field(default=None, description="解析失败原因，非空表示已降级。")


class ReportGenerat:
    def __init__(
            self,
            llm_clent: LlmClient | None=None,
        ):
        self.llm_clent=llm_clent if llm_clent is not None else LlmClient()

    def peport_generat(self, step_summary: "ExecutionSummary") -> Report:
        """生成报告。任何失败都降级成结构完整的 Report，不向外抛异常。"""
        content = ""  # 必须先初始化：大模型调用失败时 except 里还要用它
        try:
            system_prompt, user_prompt = self._build_prompt(step_summary)
            content = self.llm_clent.llm_generate_text(system_prompt, user_prompt)
            report = self._llm_res_validate(content)
            report.question = step_summary.original_question
            report.raw_content = content  # 解析成功也保留原始输出，便于排障
        # 只兜外部失败：SDK/网络(OpenAIError、OSError) 与数据问题(ValueError，
        # 覆盖 JSONDecodeError、ValidationError、空结果校验)；放过编程错误。
        except (OpenAIError, OSError, ValueError) as e:
            report = Report(
                question=step_summary.original_question,
                raw_content=content or None,  # 调用就失败时没有原始输出
                parse_error=f"{type(e).__name__}: {e}",
            )
        return report

    def _llm_res_validate(self, content: str) -> Report:
        cleaned = content.strip()
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end > start:  # 兜住模型在 JSON 前后加的解释文字
            cleaned = cleaned[start : end + 1]
        payload = json.loads(cleaned)
        report = Report.model_validate(payload)
        if not report.conclusion and not report.insights:  # 空对象/空内容="成功"但没内容
            raise ValueError("模型未返回任何结论内容")
        return report

    def _build_prompt(self, step_summary: "ExecutionSummary") -> Tuple[str, str]:
        """组装发给大模型的 (system, user) 提示词。

        入参是上一步的 ExecutionSummary：question / analysis_goal / 执行统计
        由它提供，各步骤结果从 key_findings 拼接而来。
        """
        findings = "\n".join(step_summary.key_findings).strip()
        if not findings:
            findings = "（本次分析没有任何步骤返回结果）"

        system = SYSTEM_PROMPT
        user = (
            f"用户问题：{step_summary.original_question}\n"
            f"分析目标：{step_summary.analysis_goal}\n"
            f"执行情况：{step_summary.summary_text.strip()}\n"
            "\n各步骤分析结果：\n"
            f"{findings}"
        )
        return system, user
