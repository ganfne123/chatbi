from tracemalloc import start
from unicodedata import name
import json
from ntpath import join
import os
from collections import deque
from json_schema.table_relationships import TABLE_RELATIONSHIPS
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


#广度优先算法
# def find_path(start_node, end_node, table_relationships=TABLE_RELATIONSHIPS):
#     # 创建双端队列
#     queue = deque([(start_node,[end_node])])
#     # 创建一个集合来存储已访问的节点
#     visited = {start_node}
#     while len(queue) > 0:
#         current_node, path = queue.popleft()
#         if current_node == end_node:
#             print(f"{current_node} 找到路径{path}")
#             break
#         for key,value in table_relationships.items():
#             if key != current_node: 
#                 continue
#             for relationship in value:
#                 target_node = relationship["target"]
#                 if target_node in visited:
#                     continue
#                 visited.add(target_node)
#                 new_path = path + [target_node]
#                 queue.append((target_node,new_path))
#                 if target_node == end_node:
#                     return target_node,new_path

path=['dim_customers', 'sales_orders', 'dim_products']
table_relationships=TABLE_RELATIONSHIPS
for i, anchor_path in enumerate(path[:-1]):
    for table in table_relationships[anchor_path]:
        if table["target"] == path[i + 1]:
            print(f"{anchor_path} {table['join_type']} {table['target']} on {anchor_path}.{table['fk_col']}={table['target']}.{table['pk_col']}")
            continue

