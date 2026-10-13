from dotenv import load_dotenv

import os
load_dotenv()  # 读取当前目录下的 .env 文件


# Database configuration
database_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "chatbi_mvp"),
    "charset": "utf8mb4"
}

# LLM configuration
llm_config = {
    "api_key": os.getenv("OPENAI_API_KEY",""),
    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "model": os.getenv("LLM_MODEL", "qwen3.7-plus")
}
# embedding
emd_congif ={
    "api_key": os.getenv("EMD_API_KEY",""),
    "base_url": os.getenv("EMD_BASE_URL", "https://api.openai.com/v1"),
    "model": os.getenv("EMD_LLM_MODEL", "text-embedding-v3")
}

milvus_config = {
    "uri": os.getenv("MILVUS_URI", "http://localhost:19530"),
    "user": os.getenv("MILVUS_USER", "root"),
    "password": os.getenv("MILVUS_PASSWORD", ""),   # ✅ 加默认值，返回 str
}