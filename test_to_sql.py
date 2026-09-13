
from openai import OpenAI
import re
import os
from dotenv import load_dotenv

load_dotenv()  # 读取当前目录下的 .env 文件


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

def generate_sql(query:str) ->str:
    prompt=f"请根据用户输入的语言生成对应的sql语句，用户输入为{query},只需要输出sql语句"
    responses = client.chat.completions.create(
    model=os.getenv("LLM_MODEL"),
    messages=[{"role": "user","content":prompt}],
    temperature=0.3
)
    content=responses.choices[-1].message.content
    sql=re.sub(r'```sql|```', '',content)

    return sql

if __name__ == "__main__":
    query="查询用户数量"
    print(generate_sql(query))