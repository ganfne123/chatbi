"""
验证用户输入是否有效
-输入是否为空
-输入仅为空格，换行，数字，下划线组成

"""
class QueryParser:
    """用户查询解析器"""
    def parse(self, user_input: str) -> dict:
        """解析用户输入"""
        return {
        "original_question": user_input.strip(),
        "is_valid": len(user_input.strip()) > 0
        }
    def validate(self, parsed_query: dict) -> bool:
        """校验解析结果是否有效"""
        return parsed_query.get("is_valid", False)