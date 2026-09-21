from embedding_clinet import EmbeddingClient
import numpy as np


class SearchVector:
    def __init__(self,index: dict[str,list[float]]):
        self.index=index
        print(len(index))



    def cosine_similarity(self,vec_a: list[float], vec_b: list[float]) -> float:
        a = np.array(vec_a)
        b = np.array(vec_b)
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot_product / (norm_a * norm_b))



    
    def search(self,query_embedding: list[float] , top_k=4):
        scores=[]
        for name,vector in self.index.items():
            score = self.cosine_similarity(query_embedding, vector)
            scores.append((name, score))
        # 按相似度降序排序，取 Top-K
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


if __name__=="__main__":
    embedding_client=EmbeddingClient()
    index=embedding_client.build_table_index()
    sear_client=SearchVector(index)
    querys={"2024 年各客户类型的销售收入和利润分别是多少","各部门的研发费用和销售费用占比情况如何？","按销售大区统计 2024 年统一换算成人民币的净收入，并对比订单数量和平均折扣率。"}
    for query in querys:
        query_embedding=embedding_client.get_embedding(query)
        results=sear_client.search(query_embedding)
        print(f"\nQuery: {query}")
        for name, score in results:
            print(f"  {score:.4f}  {name}")
