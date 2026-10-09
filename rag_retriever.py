import json

from pymilvus import MilvusClient
from embedding_clinet import EmbeddingClient
from config import milvus_config


class ClientMilvus:
    """Milvus 客户端封装：负责建集合、建索引、加载集合、插入数据。"""
    COLLECTION_TABLE_NAME = "table_schema_docs"
    COLLECTION_FIELD_NAME = "field_schema_docs"
    COLLECTION_INDICATOR_NAME = "indicator_knowledge"

    def __init__(self, milvus_config=milvus_config):
        self.client = MilvusClient(
            uri=milvus_config["uri"],
            token=f"{milvus_config['user']}:{milvus_config['password']}"
        )
        self.embedding = EmbeddingClient()

    def table_search(self, query: str, collection_name: str ,top_k: int =3) -> list[list[dict]]:
        """表召回：把用户问题转成向量，在表集合里检索最相似的 top_k 张表。"""
        # 1. 问题 -> 向量（1024 维，与集合里 vector 字段的 dim 一致）
        emd = self.embedding.get_embedding(query)

        res = self.client.search(
            collection_name=collection_name,
            data=[emd],             
            limit=top_k,             
            output_fields=[          
                "table_name",
                "domain",
                "page_content"
            ],
        )
        return res

    def field_search(self, query: str, collection_name: str ,top_k: int =3) ->list:
            """ 字段召回：把用户问题转成向量，在字段集合里检索最相似的 top_k 个字段。
            :param query: 用户问题
            :param collection_name: 目标集合名
            :param top_k: 返回最相似的前 K 个字段
            :return: 返回嵌套的 [[hit, ...]]，每个 hit 里包含 distance 和 entity（字段名、表名等）。
            """
            emd = self.embedding.get_embedding(query)
    
            res = self.client.search(
                collection_name=collection_name,
                data=[emd],
                limit=top_k,
                output_fields=[
                    "field_name",
                    "from_table",
                    "page_content"
                ],
            )
            return res
    def indicator_search(self, query: str, collection_name: str ,top_k: int =3) ->list:
            """ 指标召回：把用户问题转成向量，在指标集合里检索最相似的 top_k 个指标。
            :param query: 用户问题
            :param collection_name: 目标集合名
            :param top_k: 返回最相似的前 K 个指标
            :return: 返回嵌套的 [[hit, ...]]，每个 hit 里包含 distance 和 entity（指标名、定义等）。
            """
            emd = self.embedding.get_embedding(query)
    
            res = self.client.search(
                collection_name=collection_name,
                data=[emd],
                limit=top_k,
                output_fields=[
                    "name",
                    "level",
                    "definition",
                    "depends_on",
                ],
            )
            return res


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
                if rule["type"] =="whitelist":
                    results.append({rule["type"]: [parse_field(f) for f in rule["force_include"]]})
                if rule["type"] =="blacklist":
                    results.append({rule["type"]: [parse_field(f) for f in rule["force_exclude"]]})
                break   # ← 加这一行，命中就跳出，避免重复 append
    return results

def fuse_scores(embedding_hits, rule_hits, alpha=0.3, top_k=None) -> list[dict]:
    """把 Milvus 召回的字段和规则召回的字段融合成最终得分。

    final_score = (1 - alpha) * embedding_score + alpha * rule_score
    """

    # ① 收集 embedding 分数：键统一为 (表名, 字段名)
    #    Milvus 返回的 hit 里，from_table 是表名，field_name 是字段名
    embedding_scores = {}
    for layer in embedding_hits:
        # field_search 返回的是嵌套结构 [[hit, ...]]；这里兼容直接传扁平 [hit, ...]
        hits = layer if isinstance(layer, list) else [layer]
        for hit in hits:
            entity = hit["entity"]
            key = (entity["from_table"], entity["field_name"])
            # distance 就是 COSINE 相似度，直接当 embedding_score 用，不做归一化
            score = float(hit["distance"])
            # 同一字段被召回多次时，只保留最高分
            if key not in embedding_scores or score > embedding_scores[key]:
                embedding_scores[key] = score

    # ② 收集规则分数：白名单 +1，黑名单 -1
    #    同一字段若同时命中白名单和黑名单，分数会累加抵消（例如 +1 -1 = 0）
    rule_scores = {}
    for rule in rule_hits:
        for item in rule.get("whitelist", []):
            key = (item["table"], item["field"])
            rule_scores[key] = rule_scores.get(key, 0) + 1
        for item in rule.get("blacklist", []):
            key = (item["table"], item["field"])
            rule_scores[key] = rule_scores.get(key, 0) - 1

    # ③ 候选字段取并集：既包含 Milvus 召回的，也包含规则命中的
    keys = set(embedding_scores) | set(rule_scores)

    # ④ 逐字段算最终得分：final = (1 - alpha) * embedding + alpha * rule
    results = []
    for table, field in keys:
        # 缺哪一侧就按 0 处理：只被规则命中的字段 embedding_score = 0
        embedding_score = embedding_scores.get((table, field), 0.0)
        rule_score = rule_scores.get((table, field), 0)
        final_score = (1 - alpha) * embedding_score + alpha * rule_score
        results.append(
            {
                "table": table,
                "field": field,
                "embedding_score": float(embedding_score),
                "rule_score": float(rule_score),
                "final_score": float(final_score),
            }
        )

    # ⑤ 排序：final 降序；同分先看 embedding，再按表名/字段名字典序，保证结果稳定
    def sort_key(item):
        return (
            -item["final_score"],
            -item["embedding_score"],
            item["table"],
            item["field"],
        )

    results.sort(key=sort_key)

    # ⑥ 只返回得分最高的前 top_k 条；top_k 为 None 时全部返回
    if top_k is None:
        return results

    # 被规则命中的字段必须出现在最终表里，不能被 top_k 截掉：
    # 先取 top_k，再把没进 top_k 的规则命中字段补回来，最后重新排序
    kept = results[:top_k]
    kept_keys = {(item["table"], item["field"]) for item in kept}
    for item in results[top_k:]:
        key = (item["table"], item["field"])
        if key in rule_scores and key not in kept_keys:
            kept.append(item)
            kept_keys.add(key)

    kept.sort(key=sort_key)
    return kept

def run_schema_linking(
    user_query: str = "查询各大区的销售额",
    alpha: float = 0.2,
    top_k: int = 12,
) -> dict:
    """Schema Linking 全流程：表召回 -> 字段召回 -> 规则召回 -> 分数融合 -> 生成 join。

    不再直接 print，而是把结果封装成一个 dict 返回，方便上层拼进 prompt：

    {
        "query": 用户问题,
        "recalled_tables": [表名, ...],
        "table_page_content": {表名: page_content, ...},
        "fields": [
            {"table": ..., "field": ..., "embedding_score": ..., "rule_score": ...,
             "final_score": ..., "page_content": ...},
            ...
        ],
        "join_sql": join 语句字符串（无可用 join 时为空串）,
    }
    """
    client = ClientMilvus()
    # alpha：规则分数权重（越大越信规则）；top_k：只保留融合后得分最高的前 K 个字段
    # 1. Milvus 表召回
    table_res = client.table_search(
        user_query,
        collection_name=client.COLLECTION_TABLE_NAME,
        top_k=5,
    )
    recalled_tables: list[str] = []
    table_page_content: dict[str, str] = {}
    # table_search 返回嵌套的 [[hit, ...]]；每个 hit 里有 distance、table_name 和 page_content
    for hits in table_res:
        for hit in hits:
            entity = hit["entity"]
            table_name = entity["table_name"]
            if table_name not in table_page_content:
                recalled_tables.append(table_name)
            table_page_content[table_name] = entity.get("page_content", "")
    # 2. Milvus 字段召回（只保留表召回命中的表）
    field_res = client.field_search(
        user_query,
        collection_name=client.COLLECTION_FIELD_NAME,
        top_k=20,
    )
    # 只保留“表召回命中的表”下面的字段，过滤掉无关表的字段；同时记下字段的 page_content
    filtered_hits = []
    field_page_content: dict[tuple[str, str], str] = {}
    for hits in field_res:
        kept = []
        for hit in hits:
            entity = hit["entity"]
            if entity["from_table"] in recalled_tables:
                kept.append(hit)
                field_page_content[(entity["from_table"], entity["field_name"])] = entity.get(
                    "page_content", ""
                )
        filtered_hits.append(kept)
    # 3. 规则召回
    rule_hits = match_rules(user_query)
    # 4. 分数融合：final = (1 - alpha) * embedding + alpha * rule
    fused = fuse_scores(filtered_hits, rule_hits, alpha=alpha, top_k=top_k)
    # 把每个字段的 page_content 附到融合结果上
    for item in fused:
        item["page_content"] = field_page_content.get((item["table"], item["field"]), "")
    # 5. 根据表召回结果和规则召回结果，生成 join 语句
    from join_resolver import fetch_join_run
    join_results = fetch_join_run(client, user_query)

    return {
        "query": user_query,
        "recalled_tables": recalled_tables,
        "table_page_content": table_page_content,
        "fields": fused,
        "join_sql": join_results or "",
    }


def run_indicator_search(
    user_query: str = "查询已完成订单的总数量",
    top_k: int = 5,
) -> list[dict]:
    """指标召回，封装成结构化列表返回，方便拼进 prompt。

    每个召回指标会带上 depends_on；再遍历它的 depends_on，去
    json_schema/indicators_full.json 里按名字找到对应指标，一并追加进 results。

    返回：[{"name": ..., "level": ..., "definition": ..., "depends_on": [...], ...}, ...]
    """
    client = ClientMilvus()
    indicator_res = client.indicator_search(
        user_query,
        collection_name=client.COLLECTION_INDICATOR_NAME,
        top_k=top_k,
    )

    # 加载全量指标，用来按名字反查 depends_on 对应的指标
    with open("json_schema/indicators_full.json", "r", encoding="utf-8") as file:
        full_indicators = json.load(file)["indicators"]
    indicators_by_name = {item["name"]: item for item in full_indicators}

    results: list[dict] = []
    seen_names: set[str] = set()
    # indicator_search 返回嵌套的 [[hit, ...]]；每个 hit 里有 distance 和 entity
    for hits in indicator_res:
        for hit in hits:
            entity = hit.get("entity", {})
            name = entity.get("name")
            # 召回指标本身
            if name not in seen_names:
                seen_names.add(name)
                results.append(
                    {
                        "name": name,
                        "level": entity.get("level"),
                        "definition": entity.get("definition"),
                        "depends_on": entity.get("depends_on") or [],
                        "score": float(hit.get("distance", 0.0)),
                    }
                )
            # 遍历这个召回的 depends_on，去 indicators_full.json 里找对应指标，追加进 results
            for dependency_name in entity.get("depends_on") or []:
                found = indicators_by_name.get(dependency_name)
                if found and found["name"] not in seen_names:
                    seen_names.add(found["name"])
                    results.append(found)

    return results





if __name__ == "__main__":
    import json

    indicator_context = run_indicator_search("查询各大区的销售额")
    schema_context = run_schema_linking("查询各大区的销售额")

    print(json.dumps(indicator_context, ensure_ascii=False, indent=2))
    print(json.dumps(schema_context, ensure_ascii=False, indent=2))


