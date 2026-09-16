
from openai import OpenAI
import re
import os
from dotenv import load_dotenv

from build_prompt import BuildPrompt
from config import llm_config

load_dotenv()  # 读取当前目录下的 .env 文件

class LlmClient:
    def __init__(self):
        self.config=llm_config
        self.client = OpenAI(
            api_key=self.config.get("api_key",""),
            base_url=self.config["base_url"]
        )

    def generate_sql(self,query:str) ->str:
        responses = self.client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=BuildPrompt.build_prompt(query),
        temperature=0.3
    )
        content=responses.choices[-1].message.content
        sql=re.sub(r'```sql|```', '',content)

        return sql


if __name__=="__main__":
    user_quert="用户的数量"
    llm_client=LlmClient()
    request=llm_client.generate_sql(user_quert)
    print(request)
