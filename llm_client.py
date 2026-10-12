import config
from fastapi import HTTPException


from openai import OpenAI
import re
import os
from dotenv import load_dotenv

from build_prompt import build_prompt
from indicator_knowledge import IndicatorKnowledge
from config import llm_config
from typing import Generator

load_dotenv()  # 读取当前目录下的 .env 文件

class LlmClient:
    def __init__(self):
        self.config=llm_config
        self.client = OpenAI(
            api_key=self.config.get("api_key",""),
            base_url=self.config["base_url"]
        )
        self.temperature= 0.5 
        self.max_tokens=4000
        self.indicator_knowledge=IndicatorKnowledge()

    def generate_sql(self,query:str) ->str:
        system_prompt,user_prompt=build_prompt(
            query,
            use_few_shot=True,
            use_indicator=True,
            use_schema_linking=True
            )
        responses = self.llm_generate_text(system_prompt,user_prompt)
        sql=self.sql_parse(responses)
        return sql

    def generate_sql_stream(self, system_msg: str, prompt: str , temperature: float | None=None) -> Generator[str, None, None]:
        """
        调用 LLM 流式生成 SQL（逐 chunk 产出）

        每次_yield_一段增量文本，调用方可以实时推送给前端。
        流式输出结束后，调用方需要自行拼接完整 SQL 并做 markdown 代码块清理。

        Args:
            system_msg: 系统角色消息
            prompt: 完整的用户 Prompt

        Yields:
            增量文本片段（可能包含 markdown 代码块标记，需在完整拼接后统一清理）
        """
        stream = self.client.chat.completions.create(
            model=self.config["model"],
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature if temperature is None else self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            delta_content = delta.content if delta and delta.content is not None else None
            if delta_content is not None:
                yield delta_content

    def sql_parse(self,unsql: str) -> str:
        sql = re.sub(r'```sql|```', '', unsql)
        return sql


    def llm_generate_text(self, system_msg: str, prompt: str) -> str:
        """
        调用 LLM 生成普通文本（同步，一次性返回）

        Args:
            system_msg: 系统角色消息
            prompt: 完整的用户 Prompt

        Returns:
            模型返回的原始文本内容
        """
        response = self.client.chat.completions.create(
            model=self.config["model"],
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature
        )
        llm_content=response.choices[0].message.content
        if llm_content is None:
            raise ValueError("llm返回为空")
        return llm_content


    def health_check(self) -> bool :
        """通过最小对话请求检查大模型连接，返回状态和原始错误信息。"""
        try:
            self.client.chat.completions.create(
                model=self.config.get("model") or os.getenv("LLM_MODEL",""),
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
                temperature=0,
                timeout=5,
            )
            return True
        except Exception as exc:
            raise HTTPException(502,f"大模型连接错误，错误信息：{exc}")


if __name__=="__main__":
    user_quert="按客户类型统计各产品线的收入，需哎换算成人民币"
    llm_client=LlmClient()
    request=llm_client.generate_sql(user_quert)
    print(request)
