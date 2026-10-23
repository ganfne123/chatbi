from dataclasses import dataclass
from security import QuerySecurityManager
from result_formater import ResultFormatter
from database import DatabaseClient
from llm_client import LlmClient
from query_parse import QueryParser

@dataclass
class Runtime:
    query_parse : QueryParser
    llm_client : LlmClient
    database : DatabaseClient
    result_formater : ResultFormatter
    query_security_manager : QuerySecurityManager







def build_runtime() -> Runtime:
    return Runtime(
        query_parse=QueryParser(),
        llm_client=LlmClient(),
        database=DatabaseClient(),
        result_formater=ResultFormatter(),
        query_security_manager=QuerySecurityManager(),
    )