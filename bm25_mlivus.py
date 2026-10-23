from pymilvus import MilvusClient, DataType, Function, FunctionType

# 1. 连接 Milvus (假设已在本地 19530 端口运行)
client = MilvusClient(uri="http://localhost:19530",token="root:wZ:rLFaU8aXUZm2")

# 2. 定义 Schema
# 关键点：text 字段设置 enable_analyzer=True，并添加一个稀疏向量字段
schema = client.create_schema(auto_id=True, enable_dynamic_field=False)
schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
schema.add_field(
    field_name="text",
    datatype=DataType.VARCHAR,
    max_length=2000,
    enable_analyzer=True,        # 启用分词
    analyzer_params={"type": "chinese"} # 根据数据语言选择，如中文用 "chinese"
)
schema.add_field(field_name="sparse", datatype=DataType.SPARSE_FLOAT_VECTOR)

# 3. 定义 BM25 Function (实现 "Doc in, Doc out" 的关键)
bm25_function = Function(
    name="text_bm25_emb",
    input_field_names=["text"],      # 输入：原始文本
    output_field_names=["sparse"],   # 输出：Milvus 内部自动生成的稀疏向量
    function_type=FunctionType.BM25
)
schema.add_function(bm25_function)

# 4. 准备索引参数 (稀疏向量必须使用 BM25 度量)
index_params = client.prepare_index_params()
index_params.add_index(
    field_name="sparse",
    index_type="AUTOINDEX",          # 或 "SPARSE_INVERTED_INDEX"
    metric_type="BM25"               # 指定 BM25 度量
)

# 5. 创建 Collection
collection_name = "bm25_demo"
client.create_collection(
    collection_name=collection_name,
    schema=schema,
    index_params=index_params
)

# 6. 插入数据 (只需传原始文本，无需手动转换向量)
# data = [
#     {"text": "苹果手机电池续航怎么样"},
#     {"text": "iPhone 15 测评与使用体验"},
#     {"text": "特斯拉 Model 3 的续航里程"},
#     {"text": "如何更换笔记本电池"}
# ]
# client.insert(collection_name=collection_name, data=data)

# 7. 执行全文检索 (直接传查询文本)
search_res = client.search(
    collection_name=collection_name,
    data=["电脑"],       # 查询文本
    anns_field="sparse",              # 指定在稀疏向量字段上搜索
    limit=2,
    output_fields=["text"]            # 返回原始文本
)

# 8. 打印结果
for hits in search_res:
    for hit in hits:
        print(f"score: {hit['distance']:.4f}, text: {hit['entity']['text']}")