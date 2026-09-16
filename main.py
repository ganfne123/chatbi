import result_formater
import query_parse
import sys
from query_parse import QueryParser
from build_prompt import BuildPrompt
from llm_client import LlmClient
from database import DatabaseClient
from result_formater import ResultFormatter


class ChatBiSystem:
    def __init__(self):
        self.query_parse=QueryParser()
        self.llm_client=LlmClient()
        self.database=DatabaseClient()
        self.result_formater=ResultFormatter()


    def run(self,query : str):
        parse=self.query_parse.parse(query)
        if not self.query_parse.validate(parse):
            return {"success": False, "error": "输入问题为空"}

        sql=self.llm_client.generate_sql(query)
        columns,data=self.database.execute(sql)
        result=self.result_formater.format(columns,data)
        return {
            "success": True,
            "sql": sql,
            "columns": columns,
            "results": data,
            "formatted": result
            }

def main():
    chat=ChatBiSystem()
    query=input("输入")    
    result=chat.run(query)
    print(result)

if __name__=="__main__":
    main()

