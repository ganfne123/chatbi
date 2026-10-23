import json
import time
from datetime import datetime
from query_parse import QueryParser
from llm_client import LlmClient
from database import DatabaseClient
from result_formater import ResultFormatter
from security import QuerySecurityManager, UserContext
from typing import Generator

class ChatBiSystem:
    def __init__(
            self,
            query_parse: QueryParser | None=None,
            llm_client: LlmClient | None=None
        ):
        self.query_parse=query_parse or QueryParser()
        self.llm_client=llm_client or LlmClient()
        self.database=DatabaseClient()
        self.result_formater=ResultFormatter()
        self.query_security_manager=QuerySecurityManager()


    def run(self,query : str, user_contest: UserContext , error_info: dict | None=None) ->dict:
        started_at = time.perf_counter()
        parse=self.query_parse.parse(query)
        if not self.query_parse.validate(parse):
            return {
                "success": False,
                "error": "输入问题为空",
                "error_type": "validation"
            }

        try:
            if error_info:
                request=self.llm_client.generate_sql(query,error_info=error_info)
            else:
                request=self.llm_client.generate_sql(query)
            sql=self.query_security_manager.secure_sql(request,user_contest)
            sql_generation_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )
        except Exception as e:
            return{
                "success" : False,
                "error" : str(e),
                "error_type": "generate_sql_error"
            }
        try:
            columns,data=self.database.execute(sql)
            columns,masked_data=self.query_security_manager.mask_result(columns,data,user_contest)
        except Exception as e:
            return{
                "success" : False,
                "error" : str(e),
                "error_type": "database_execute_error",
                # 带上失败的 SQL：重试时要把它回喂给模型，否则模型看不到自己上次写了什么
                "sql": sql
            }
        result=self.result_formater.format(columns,masked_data)
        total_ms = round((time.perf_counter() - started_at) * 1000, 2)
        return {
            "success": True,
            "question": query,
            "sql": sql,
            "columns": columns,
            "data": masked_data,
            "formatted": result,
            "metadata": {
                "sql_generation_ms": sql_generation_ms,
                "total_ms": total_ms,
            },
        }


    def _sse_event(self, event_type: str, data: dict) -> str:
        payload = json.dumps(data, ensure_ascii=False)
        body = "".join(f"data: {line}\n" for line in payload.split("\n"))
        return f"event: {event_type}\n{body}\n"

    def run_stream(self, query: str) -> Generator[str, None, None]:
        print("解析用户问题"+datetime.now().strftime("%H:%M:%S"))
        parsed = self.query_parse.parse(query)
        if not self.query_parse.validate(parsed):
            yield self._sse_event("error", {"error": "输入问题为空", "error_type": "validation"})
            return

        chunk_complete = []
        try:
            for chunk in self.llm_client.generate_sql_stream(query):
                chunk_complete.append(chunk)
                yield self._sse_event("chunk", {"content": chunk})
        except Exception as e:
            yield self._sse_event("error", {"error": str(e), "error_type": "generate_sql_error"})
            return

        complete_sql = "".join(chunk_complete)
        sql = self.llm_client.sql_parse(complete_sql)
        yield self._sse_event("complete_sql", {"sql": sql})

        try:
            columns, data = self.database.execute(sql)
        except Exception as e:
            yield self._sse_event("error", {"error": str(e), "error_type": "database_error"})
            return

        result = self.result_formater.format(columns, data)
        yield self._sse_event("result", {
            "columns": columns,
            "rows": result,
            "row_count": len(data),
        })

def main():
    chat=ChatBiSystem()
    query=input("输入")
    result=chat.run(query)
    print(result)

if __name__=="__main__":
    main()
