from pandas.core.ops.docstrings import key
from unicodedata import name
import json
from ntpath import join
import os
# path=os.path.join("src","new_chatbi","_init_.py")
# # print(path)


# path_table=os.path.join("json_schema","table_scheam.json")
# path_field=os.path.join("json_schema","scheam_field.json")



# pwd=os.getcwd()
# # print(pwd)

# path=os.path.join("pormpt.json")
# with open(path_field,"rb") as file:
#     data=file.read()
# text=data.decode("utf-8")
# dict=json.loads(text)
# for key, value in dict.items():
# with open(path_table,"r", encoding="utf-8") as file:
#     test=file.read()
# data=json.loads(test)



# rows = []
# for chunk in data:
#     for key , value in chunk.items():
    # print(key,value)    

# nest: str ="我要查询毛利率"
# a="你是个毛"
# if a in nest:
#     print(a)

# from pymilvus import MilvusClient,DataType

# client=MilvusClient(
#     uri="http://localhost:19530",
#     user="root",
#     password="wZ:rLFaU8aXUZm2"
# )
# schema=client.create_schema(
#     auto_id=False,
#     enable_dynamic_field=True,
# )
# schema.add_field(field_name="my_id", datatype=DataType.INT64, is_primary=True)
# schema.add_field(field_name="my_vector", datatype=DataType.FLOAT_VECTOR, dim=5)
# schema.add_field(field_name="my_varchar", datatype=DataType.VARCHAR, max_length=512)


# index_params=client.prepare_index_params()
# index_params.add_index(
#     field_name="my_id",
#     index_type="AUTOINDEX"
# )
# index_params.add_index(
#     field_name="my_vector",
#     index_type="AUTOINDEX",
#     metric_type="COSINE"     # 根据用途选择，如 L2 / IP / COSINE
# )

# # client.create_collection(
# #     collection_name="customized_setup_1",
# #     schema=schema,
# #     index_params=index_params
# # )

# res=client.get_load_state(
#     collection_name="customized_setup_1"
# )

# client.create_partition(
#     collection_name="customized_setup_1",
#     partition_name="my_database_1_partition_1"
# )
# res1= client.list_partitions(
#     collection_name="customized_setup_1"
# )
# print(res,f"res2:{res1}")
# print(type(schema))

