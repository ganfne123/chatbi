from pathlib import Path
from pydantic import BaseModel, Field
from pymilvus import MilvusClient, DataType
from embedding_clinet import EmbeddingClient
import json
import re


class TableDesSchema(BaseModel):
    table_name: str = Field(..., description="表名")
    vector: list[float] = Field(..., description="表名描述的向量")
    page_content: str = Field(..., description="表名描述的原文本")
    domain: str
    key_fields: str


class fieldDesSchema(BaseModel):
    field_name: str = Field(..., description=" 字段名")
    vector: list[float] = Field(..., description="字段描述的向量")
    page_content: str = Field(..., description="字段描述的原文本")
    from_table: str = Field(...,description="来自哪张表")


path_table=Path("json_schema/table_scheam.json")
path_field=Path("json_schema/scheam_field.json")



class ClientMilvus:
    """Milvus 客户端封装：负责建集合、建索引、加载集合、插入数据。"""

    COLLECTION_TABLE_NAME = "table_schema_docs"
    COLLECTION_FIELD_NAME = "field_schema_docs"

    def __init__(self):
        self.client = MilvusClient(
            uri="http://localhost:19530",
            token="root:wZ:rLFaU8aXUZm2"
        )
        self.embedding = EmbeddingClient()

    def create_collection_table(self, table_name: str = COLLECTION_TABLE_NAME):
        """
        创建用于存放表结构描述的集合，并建好索引、加载到内存。

        :param table_name: 集合名称，默认 "table_schema_docs"
        """
        schema = self.client.create_schema()
        index_params = self.client.prepare_index_params()

        schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field("table_name", DataType.VARCHAR, max_length=256)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field("page_content", DataType.VARCHAR, max_length=8192)
        schema.add_field("domain", DataType.VARCHAR, max_length=128)
        schema.add_field("key_fields", DataType.VARCHAR, max_length=4096)

        index_params.add_index("vector", "AUTOINDEX", metric_type="COSINE")

        if self.client.has_collection(table_name):
            self.client.drop_collection(table_name)

        self.client.create_collection(
            table_name,
            schema=schema,
            index_params=index_params
        )
        self.client.load_collection(table_name)


    def create_collection_field(self, table_name: str = COLLECTION_FIELD_NAME):
            """
            创建用于存放表结构描述的集合，并建好索引、加载到内存。
    
            :param table_name: 集合名称，默认 "table_schema_docs"
            """
            schema = self.client.create_schema()
            index_params = self.client.prepare_index_params()
    
            schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
            schema.add_field("field_name", DataType.VARCHAR, max_length=256)
            schema.add_field("vector", DataType.FLOAT_VECTOR, dim=1024)
            schema.add_field("page_content", DataType.VARCHAR, max_length=8192)
            schema.add_field("from_table", DataType.VARCHAR, max_length=256)

    
            index_params.add_index("vector", "AUTOINDEX", metric_type="COSINE")
    
            if self.client.has_collection(table_name):
                self.client.drop_collection(table_name)
    
            self.client.create_collection(
                table_name,
                schema=schema,
                index_params=index_params
            )
            self.client.load_collection(table_name)

    

    def insert_table_data(self, path_table: Path=Path("json_schema/table_scheam.json"), collection_name: str = COLLECTION_TABLE_NAME):
        """
        把表结构描述批量向量化后插入 Milvus。

        :param table_list: teble_schema 这样的列表
        :param collection_name: 目标集合名
        """
        data={}
        with open(path_table,"r", encoding="utf-8") as file:
            test=file.read()
        data=json.loads(test)


        
        rows = []
        for chunk in data:
            emd = self.embedding.get_embedding(chunk["page_content"])
            data = TableDesSchema(
                table_name=chunk["table_name"],
                vector=emd,
                page_content=chunk["page_content"],
                domain=chunk["domain"],
                key_fields=",".join(chunk["key_fields"]),
            )
            rows.append(data.model_dump())

        res = self.client.insert(collection_name=collection_name, data=rows)
        return res
    
    def insert_field_data(self,  Path=Path("json_schema/scheam_field.json"), collection_name: str = COLLECTION_FIELD_NAME):
            """
            把表结构描述批量向量化后插入 Milvus。
    
            :param table_list: teble_schema 这样的列表
            :param collection_name: 目标集合名
            """
            data={}
            rows=[]
            with open(path_field,"rb") as file:
                data=file.read()
            text=data.decode("utf-8")
            dict=json.loads(text)
            for key, value in dict.items():
                match= re.search(r"\.([^.]+)$", key)
                if not match:
                    continue
                field_table = match.group(1)
                emd=self.embedding.get_embedding(value["description"])
                field=fieldDesSchema(
                    field_name=field_table,
                    vector=emd,
                    page_content=value["description"],
                    from_table=value["table"]
                )
                rows.append(field.model_dump())
    
            res = self.client.insert(collection_name=collection_name, data=rows)
            return res

    def table_search(self, query: str, collection_name: str ,top_k: int =3):
        emd = self.embedding.get_embedding(query)

        res = self.client.search(
            collection_name=collection_name,
            data=[emd],
            limit=top_k,
            output_fields=[
                "table_name",
            ],
        )
        return res

    def field_search(self, query: str, collection_name: str ,top_k: int =3):
            emd = self.embedding.get_embedding(query)
    
            res = self.client.search(
                collection_name=collection_name,
                data=[emd],
                limit=top_k,
                output_fields=[
                    "field_name",
                    "from_table"
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
                results.append({
                    "whitelist": [parse_field(f) for f in rule["force_include"]],
                    "blacklist": [parse_field(f) for f in rule["force_exclude"]],
                })
                break   # ← 加这一行，命中就跳出，避免重复 append
    return results

def fuse_scores(embedding_hits, rule_hits, alpha=0.3, top_k=None) -> list[dict]:
    """把 Milvus 召回的字段和规则召回的字段融合成最终得分。

    final_score = (1 - alpha) * embedding_score + alpha * rule_score

    Args:
        embedding_hits: field_search(...) 的原始返回（嵌套的 [[hit, ...]]），
            hit 形如 {"distance": float, "entity": {"field_name", "from_table"}}。
        rule_hits: match_rules(...) 的返回，形如
            [{"whitelist": [{"table", "field"}], "blacklist": [...]}]。
        alpha: 规则分数权重，默认 0.3。
        top_k: 返回 final_score 最高的前 K 条；被规则命中的字段一定会保留，
            不会被 top_k 截掉；None 表示全部返回。

    Returns:
        按 final_score 降序排列的列表，每项形如
        {"table": ..., "field": ..., "embedding_score": ...,
         "rule_score": ..., "final_score": ...}。
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


if __name__ == "__main__":
    # 端到端演示：向量召回 -> 规则召回 -> 分数融合
    client = ClientMilvus()
    # client.create_collection_table()
    # client.insert_table_data()
    # client.create_collection_field()
    # client.insert_field_data()

    # 演示用的两个问题：前者体现白名单加分，后者体现白/黑名单互相抵消
    querys = ["查询各大区的销售额", "含税收入是多少"]
    # alpha：规则分数权重（越大越信规则）；top_k：只展示融合后得分最高的前 K 个字段
    alpha = 0.2
    top_k = 12

    for query in querys:
        print(f"\n{'=' * 64}")
        print(f"Query: {query}")
        print("=" * 64)

        # 1. Milvus 表召回
        table_res = client.table_search(
            query,
            collection_name=client.COLLECTION_TABLE_NAME,
            top_k=5,
        )
        print("\n[1] Milvus 表召回：")
        recalled_tables = []
        # table_search 返回嵌套的 [[hit, ...]]；每个 hit 里有 distance 和 table_name
        for hits in table_res:
            for hit in hits:
                table_name = hit["entity"]["table_name"]
                recalled_tables.append(table_name)
                print(f"    {hit['distance']:.4f}  {table_name}")

        # 2. Milvus 字段召回（只保留表召回命中的表）
        field_res = client.field_search(
            query,
            collection_name=client.COLLECTION_FIELD_NAME,
            top_k=20,
        )
        print("\n[2] Milvus 字段召回：")
        # 只保留“表召回命中的表”下面的字段，过滤掉无关表的字段
        filtered_hits = []
        for hits in field_res:
            kept = [
                hit
                for hit in hits
                if hit["entity"]["from_table"] in recalled_tables
            ]
            filtered_hits.append(kept)
            for hit in kept:
                print(
                    f"    {hit['distance']:.4f}  "
                    f"{hit['entity']['from_table']}.{hit['entity']['field_name']}"
                )

        # 3. 规则召回
        rule_hits = match_rules(query)
        print("\n[3] 规则召回：")
        print(f"    {json.dumps(rule_hits, ensure_ascii=False)}")

        # 4. 分数融合：final = (1 - alpha) * embedding + alpha * rule
        fused = fuse_scores(filtered_hits, rule_hits, alpha=alpha, top_k=top_k)
        print(f"\n[4] 融合结果（alpha={alpha}，top_k={top_k}）：")
        # 输出四列：字段、向量分、规则分（白名单+1/黑名单-1）、按公式算出的最终分
        print(f"    {'表.字段':<36}{'embedding':>12}{'rule':>8}{'final':>10}")
        print(f"    {'-' * 36}{'-' * 12}{'-' * 8}{'-' * 10}")
        for item in fused:
            name = f"{item['table']}.{item['field']}"
            print(
                f"    {name:<36}{item['embedding_score']:>12.4f}"
                f"{item['rule_score']:>8.1f}{item['final_score']:>10.4f}"
            )
