from json_schema.rules_json import BUSINESS_RULES


def parse_field(full_name: str) -> dict:
    """把 'sales_orders.net_amount' 拆成 {'table': ..., 'field': ...}"""
    if "." not in full_name:
        return {"table": None, "field": full_name}
    table, field = full_name.split(".", 1)
    return {"table": table, "field": field}


def match_rules(query: str) -> list[dict]:
    """根据用户问题匹配业务规则，返回对应的表和字段。
    """
    if not isinstance(query, str):
        raise TypeError("query 必须是字符串")
    if not query:
        return []

    results = []

    for rule in BUSINESS_RULES:
        for keyword in rule["trigger_keywords"]:
            if keyword in query:
                results.append({
                    "whitelist": [parse_field(f) for f in rule["force_include"]],
                    "blacklist": [parse_field(f) for f in rule["force_exclude"]],
                })
                break   # ← 加这一行，命中就跳出，避免重复 append
    return results

def main() -> None:
    """交互式查看规则匹配的全过程。"""
    query = input("请输入查询: ").strip()

    print(f"\n用户问题：{query!r}")
    print(f"共 {len(BUSINESS_RULES)} 条业务规则，开始逐条匹配……")

    for index, rule in enumerate(BUSINESS_RULES, start=1):
        keywords = rule["trigger_keywords"]
        hits = [keyword for keyword in keywords if keyword in query]



   

    print("\n匹配结果：")
    results = match_rules(query)
    print(results)



if __name__ == "__main__":
    main()
