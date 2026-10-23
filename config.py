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


switch= {
        "few_shot": os.getenv("FEATURE_FEW_SHOT", "true").lower() == "true",
        "rules": os.getenv("FEATURE_RULES", "true").lower() == "true",
        "guards": os.getenv("FEATURE_GUARDS", "true").lower() == "true",
        "indicator_knowledge": os.getenv("FEATURE_INDICATOR_KNOWLEDGE", "true").lower() == "true",
        "schema_linking": os.getenv("FEATURE_SCHEMA_LINKING", "false").lower() == "true",
        "indicator_rag": os.getenv("FEATURE_INDICATOR_RAG", "false").lower() == "true",
    }




"""
配置管理模块

收拢环境配置、运行配置和功能开关，减少主链路里的硬编码默认值。
"""


import copy
import os

from dotenv import load_dotenv

load_dotenv()


def _build_default_db_source() -> dict[str, object]:
    return {
        "driver": os.getenv("DB_DRIVER", "mysql"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 3307)),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "123456"),
        "database": os.getenv("DB_NAME", "chatbi_mvp"),
        "charset": "utf8mb4",
        "autocommit": True,
        "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", 5)),
        "read_timeout": int(os.getenv("DB_READ_TIMEOUT", 8)),
        "write_timeout": int(os.getenv("DB_WRITE_TIMEOUT", 8)),
    }


APP_CONFIG = {
    "environment": os.getenv("APP_ENV", "dev"),
    "database": {
        "default_source": os.getenv("DB_DEFAULT_SOURCE", "mysql_main"),
        "sources": {
            os.getenv("DB_DEFAULT_SOURCE", "mysql_main"): _build_default_db_source(),
        },
        "runtime": {
            "pool_size": int(os.getenv("DB_POOL_SIZE", 5)),
            "max_overflow": int(os.getenv("DB_POOL_MAX_OVERFLOW", 5)),
            "pool_timeout": float(os.getenv("DB_POOL_TIMEOUT", 3)),
            "slow_query_threshold_ms": float(os.getenv("DB_SLOW_QUERY_THRESHOLD_MS", 200)),
        },
    },
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "model": os.getenv("LLM_MODEL", "gpt-4"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
        "temperature": 0.1,
        "max_tokens": int(os.getenv("LLM_MAX_TOKENS", 4000)),
    },
    "features": {
        "few_shot": os.getenv("FEATURE_FEW_SHOT", "true").lower() == "true",
        "rules": os.getenv("FEATURE_RULES", "true").lower() == "true",
        "guards": os.getenv("FEATURE_GUARDS", "true").lower() == "true",
        "indicator_knowledge": os.getenv("FEATURE_INDICATOR_KNOWLEDGE", "true").lower() == "true",
        "schema_linking": os.getenv("FEATURE_SCHEMA_LINKING", "false").lower() == "true",
        "indicator_rag": os.getenv("FEATURE_INDICATOR_RAG", "false").lower() == "true",
    },
}


def get_database_source_config(
    source_id: str | None = None,
    app_config: dict | None = None,
) -> dict[str, object]:
    """返回指定数据源的配置，默认取当前应用默认数据源。"""
    config = app_config or APP_CONFIG
    database_config = config["database"]
    resolved_source_id = source_id or database_config["default_source"]
    source = database_config["sources"].get(resolved_source_id)
    if source is None:
        raise KeyError(f"Unknown database source: {resolved_source_id}")
    return copy.deepcopy(source)


DB_CONFIG = get_database_source_config()
DB_RUNTIME_CONFIG = APP_CONFIG["database"]["runtime"]
LLM_CONFIG = APP_CONFIG["llm"]
