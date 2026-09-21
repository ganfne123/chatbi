from fastapi import HTTPException
from datetime import datetime


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
        self.indicator_knowledge=IndicatorKnowledge()

    def generate_sql(self,query:str) ->str:
        print("llm开始生产sql"+datetime.now().strftime("%H:%M:%S"))
        knowledge=self.indicator_knowledge.get_knowledge(query)
        responses = self.client.chat.completions.create(
        model=os.getenv("LLM_MODEL",""),
        messages=build_prompt(query,konwledge=knowledge),
        temperature=0.3,
    )
        print("llm生产sql完毕"+datetime.now().strftime("%H:%M:%S"))
        if not responses.choices:
            raise RuntimeError("大模型响应中没有 choices")
        content = responses.choices[0].message.content
        assert isinstance(content,str)
        return content

    def generate_sql_stream(self,query:str) ->Generator[str, None, None]:
        knowledge=self.indicator_knowledge.get_knowledge(query)
        responses = self.client.chat.completions.create(
        model=os.getenv("LLM_MODEL",""),
        messages=build_prompt(query,konwledge=knowledge),
        temperature=0.3,
        stream=True,
    )
        for chunk in responses:
            if not chunk.choices:
                continue
            data = chunk.choices[0].delta.content
            if data:
                yield data

    def sql_parse(self,unsql: str) -> str:
        sql = re.sub(r'```sql|```', '', unsql)
        return sql



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
    user_quert="根据客户类型查看利润"
    llm_client=LlmClient()
    request=llm_client.generate_sql_stream(user_quert)
    print(request)
