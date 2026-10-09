from pymilvus import MilvusClient,DataType
from config import milvus_config
from embedding_clinet import EmbeddingClient
from pydantic import BaseModel, Field
import json

class Indicator:
    def __init__(self, name: str, level: str, definition: str,definition_vector: list[float],depends_on: str):
        self.name: str = name
        self.level: str = level
        self.definition: str = definition
        self.depends_on: str =depends_on
        self.definition_vector: list[float] = definition_vector  # 用于存储向量化后的 definition 字段

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
    domain: str = Field(...,description="表的分类")



class CreateMilvusCollection:
    COLLECTION_TABLE_NAME = "table_schema_docs"
    COLLECTION_FIELD_NAME = "field_schema_docs"
    COLLECTION_INDICATOR_NAME = "indicator_knowledge"
    def __init__(self):
        self.config=milvus_config
        self.client = MilvusClient(uri=self.config["uri"], user=self.config["user"], password=self. config["password"])
        self.embedding_client = EmbeddingClient()

    def create_indicator_collection(self,indicator_collection_name: str=COLLECTION_INDICATOR_NAME):
        """创建指标知识集合，并插入数据"""
        # 创建集合
        schema = self.client.create_schema()
        index_params = self.client.prepare_index_params()

        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field(field_name="name", datatype=DataType.VARCHAR, max_length=512)
        schema.add_field(field_name="level", datatype=DataType.VARCHAR, max_length=1024)
        schema.add_field(field_name="definition_vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        schema.add_field(field_name="definition", datatype=DataType.VARCHAR, max_length=1024)
        schema.add_field(field_name="depends_on", datatype=DataType.JSON, max_length=1024)


        index_params.add_index(field_name="definition_vector", index_type="AUTOINDEX",metric_type="COSINE")

        self.client.create_collection(
            collection_name=indicator_collection_name,
            schema=schema,
            index_params=index_params
        )


    def get_data(self, path: str)-> list[dict]:
        """从指定路径加载 JSON 数据"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["indicators"]  

    def drop_collection(self, collection_name: str=COLLECTION_INDICATOR_NAME):
        self.client.drop_collection(collection_name=collection_name)

    def insert_indicator_data(self,data: list[dict], collection_name: str=COLLECTION_INDICATOR_NAME):
        """将数据插入指定集合"""
        for record in data:
            definition_vector = self.embedding_client.get_embedding(record.get("definition", ""))
            indicator = Indicator(
                name=record.get("name",""),
                level=record.get("level",""),
                definition=record.get("definition",""),
                definition_vector=definition_vector,
                depends_on=record.get("depends_on","")
            )
            self.client.insert(
                collection_name=collection_name,
                data=indicator.__dict__
            )
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
            schema.add_field("domain",DataType.VARCHAR, max_length=256)

    
            index_params.add_index("vector", "AUTOINDEX", metric_type="COSINE")
    
            if self.client.has_collection(table_name):
                self.client.drop_collection(table_name)
    
            self.client.create_collection(
                table_name,
                schema=schema,
                index_params=index_params
            )
            self.client.load_collection(table_name)

    

    def insert_table_data(self, collection_name: str = COLLECTION_TABLE_NAME):
        """
        把表结构描述批量向量化后插入 Milvus。

        :param table_list: teble_schema 这样的列表
        :param collection_name: 目标集合名
        """
        from json_schema.table_scheam import TABLE_METADATA
        data=TABLE_METADATA  
        rows = []
        for key,chunk in data.items():
            emd = self.embedding_client.get_embedding(chunk["description"])
            data = TableDesSchema(
                table_name=key,
                vector=emd,
                page_content=chunk["description"],
                domain=chunk["domain"],
                key_fields=",".join(chunk["key_fields"]),
            )
            rows.append(data.model_dump())

        res = self.client.insert(collection_name=collection_name, data=rows)
        return res
    
    def insert_field_data(self, collection_name: str = COLLECTION_FIELD_NAME):
            """
            把表结构描述批量向量化后插入 Milvus。
    
            :param table_list: teble_schema 这样的列表
            :param collection_name: 目标集合名
            """
            from json_schema.scheam_field import FIELD_METADATA
            rows=[]
            dict=FIELD_METADATA
            for key, value in dict.items():
                field_table = value["field"]
                emd=self.embedding_client.get_embedding(value["description"])
                field=fieldDesSchema(
                    field_name=field_table,
                    vector=emd,
                    page_content=value["description"],
                    from_table=value["table"],
                    domain=value["domain"]
                )
                rows.append(field.model_dump())
    
            res = self.client.insert(collection_name=collection_name, data=rows)
            return res
    
    def create_indicator_collection_run(self):
        """执行创建集合、插入数据的完整流程"""
        # 1. 加载数据
        data = self.get_data("json_schema/indicators_full.json")

        # 2. 删除已有集合（如果存在）
        self.drop_collection("indicator_knowledge")

        # 3. 创建集合并插入数据
        self.create_indicator_collection(indicator_collection_name="indicator_knowledge")

        self.insert_indicator_data(collection_name="indicator_knowledge", data=data)
        print("指标知识集合创建并插入数据完成。")

    def create_table_collection_run(self):
        """执行创建表结构集合、插入数据的完整流程"""
        # 1. 删除已有集合（如果存在）
        self.drop_collection(self.COLLECTION_TABLE_NAME)

        # 2. 创建集合并插入数据
        self.create_collection_table(table_name=self.COLLECTION_TABLE_NAME)
        self.insert_table_data(collection_name=self.COLLECTION_TABLE_NAME)
        print("表结构集合创建并插入数据完成。")


    def create_field_collection_run(self):
        """执行创建字段结构集合、插入数据的完整流程"""
        # 1. 删除已有集合（如果存在）
        self.drop_collection(self.COLLECTION_FIELD_NAME)

        # 2. 创建集合并插入数据
        self.create_collection_field(table_name=self.COLLECTION_FIELD_NAME)
        self.insert_field_data(collection_name=self.COLLECTION_FIELD_NAME)
        print("字段结构集合创建并插入数据完成。")
if __name__ == "__main__":
    create_milvus = CreateMilvusCollection()
    # 创建指标知识集合并插入数据
    create_milvus.create_indicator_collection_run()
    # # 创建表结构集合并插入数据
    # create_milvus.create_table_collection_run()
    # # 创建字段结构集合并插入数据
    # create_milvus.create_field_collection_run()
