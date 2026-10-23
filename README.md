# ChatBI 智能问数

基于自然语言生成 SQL 的数据分析系统，提供 Web 对话界面、流式查询、多步骤 Agent 分析报告、RAG 检索、SQL 安全校验和结果脱敏能力。

## 功能特性

- **自然语言问数**：将业务问题转换为 MySQL 查询并返回表格结果。
- **流式响应**：通过 SSE 实时返回 SQL 生成过程、执行结果和错误信息。
- **Agent 分析**：自动拆解问题、规划步骤、执行查询、汇总洞察并生成分析报告。
- **RAG 增强**：支持 Schema Linking、表关系召回、指标知识检索和 Join 路径推理。
- **安全控制**：仅允许查询类 SQL，支持行级过滤、敏感字段脱敏和登录 Token 校验。
- **开箱即用的 Web 界面**：Vue + Tailwind CSS + ECharts，本地静态资源，不依赖外部 CDN。

## 技术栈

- Python 3.12+
- FastAPI / Uvicorn
- MySQL
- Milvus
- OpenAI 兼容 API
- Vue 3、Tailwind CSS、ECharts

## 处理流程

```text
Web / API
   │
   ▼
FastAPI ──> ChatBiSystem
              │
              ├── 输入校验
              ├── Prompt 构建
              │     ├── Few-shot
              │     ├── Schema Linking / Join 推理
              │     └── 指标知识检索
              ├── LLM 生成 SQL
              ├── SQL 安全校验与行级过滤
              ├── MySQL 执行
              └── 结果格式化与字段脱敏

Agent 模式：
问题拆解 ──> 步骤规划 ──> 查询执行 / 失败修复重试 ──> 结果汇总 ──> 分析报告
```

## 项目结构

```text
.
├── api_server.py             # FastAPI 服务、认证与查询接口
├── main.py                   # ChatBI 核心执行流程
├── agnet_main.py             # Agent 模式入口
├── agnet_planner.py          # 问题拆解、步骤执行与结果汇总
├── llm_client.py             # OpenAI 兼容客户端与 SQL 生成
├── build_prompt.py           # Prompt、Few-shot 与修复指令构建
├── rag_retriever.py          # Schema / 指标向量召回
├── join_resolver.py          # 表关系图与 Join 路径推理
├── security.py               # SQL 安全校验与结果脱敏
├── utils.py                  # 登录、密码哈希与 Token 校验
├── config.py                 # 环境变量与运行配置
├── database.py               # MySQL 客户端
├── streamlit_app.py          # 旧版 Streamlit 界面
├── frontend/
│   ├── index.html            # Web 单页
│   └── vendor/               # Vue、Tailwind、ECharts 本地依赖
└── json_schema/              # 表结构、字段、关系与指标配置
```

## 环境要求

启动前请准备：

1. Python 3.12 或更高版本。
2. [uv](https://docs.astral.sh/uv/) 包管理器。
3. MySQL 数据库和可访问的业务数据表。
4. Milvus 服务及已初始化的表、字段、指标向量集合。
5. 一个兼容 OpenAI Chat Completions 协议的大模型服务。
6. 一个兼容 OpenAI Embeddings 协议的向量化服务。

## 快速开始

### 1. 安装依赖

```bash
git clone https://github.com/ganfne123/chatbi.git
cd chatbi
uv sync
```

### 2. 配置环境变量

在项目根目录创建 `.env`：

```dotenv
# LLM
OPENAI_API_KEY=your-llm-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# Embedding
EMD_API_KEY=your-embedding-api-key
EMD_BASE_URL=https://api.openai.com/v1
EMD_LLM_MODEL=text-embedding-v3

# MySQL
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-db-password
DB_NAME=chatbi_mvp

# Milvus
MILVUS_URI=http://127.0.0.1:19530
MILVUS_USER=root
MILVUS_PASSWORD=your-milvus-password

# 功能开关
FEATURE_FEW_SHOT=true
FEATURE_RULES=true
FEATURE_GUARDS=true
FEATURE_INDICATOR_KNOWLEDGE=true
FEATURE_SCHEMA_LINKING=false
FEATURE_INDICATOR_RAG=false
```

`.env` 已被 `.gitignore` 忽略，请勿提交真实密钥。生产环境建议通过部署平台的 Secret 管理功能注入。

### 3. 初始化外部依赖

当前仓库不包含数据库迁移脚本。运行前需要确保以下内容已准备好：

- MySQL 中存在业务表，并已在 `json_schema/` 中维护对应表结构、字段和关联关系。
- 认证相关表已创建：
  - `user`：至少包含 `id`、`username`、`password`、`role`
  - `user_token`：至少包含 `id`、`user_name`、`token`、`expires_at`
  - `role`：至少包含 `id`、`name`
  - `role_row_filter`：至少包含 `role_id`、`table_name`、`column_name`
  - `role_masked_column`：至少包含 `role_id`、`column_name`
- Milvus 中存在系统使用的表和指标向量集合；具体集合名称与字段定义见 `rag_retriever.py`、`reacte_mlivus_collection.py`。

如果暂时没有准备 Milvus，可关闭 RAG 相关开关：

```dotenv
FEATURE_INDICATOR_KNOWLEDGE=false
FEATURE_SCHEMA_LINKING=false
FEATURE_INDICATOR_RAG=false
```

### 4. 启动服务

```bash
uv run uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：

- Web 界面：<http://127.0.0.1:8000/>
- OpenAPI 文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>

## 环境变量说明

| 变量 | 必填 | 说明 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 是 | LLM API Key |
| `OPENAI_BASE_URL` | 是 | OpenAI 兼容 API 地址 |
| `LLM_MODEL` | 是 | 用于生成 SQL 和分析报告的模型名称 |
| `EMD_API_KEY` | 是 | Embedding API Key |
| `EMD_BASE_URL` | 是 | Embedding API 地址 |
| `EMD_LLM_MODEL` | 是 | Embedding 模型名称 |
| `DB_HOST` | 是 | MySQL 地址 |
| `DB_PORT` | 是 | MySQL 端口，默认 `3306` |
| `DB_USER` | 是 | MySQL 用户名 |
| `DB_PASSWORD` | 是 | MySQL 密码 |
| `DB_NAME` | 是 | 数据库名称 |
| `MILVUS_URI` | 是 | Milvus 地址 |
| `MILVUS_USER` | 是 | Milvus 用户名 |
| `MILVUS_PASSWORD` | 是 | Milvus 密码 |
| `FEATURE_FEW_SHOT` | 否 | 是否启用 Few-shot，默认 `true` |
| `FEATURE_RULES` | 否 | 是否启用业务规则，默认 `true` |
| `FEATURE_GUARDS` | 否 | 是否启用错误防护，默认 `true` |
| `FEATURE_INDICATOR_KNOWLEDGE` | 否 | 是否启用指标知识检索，默认 `true` |
| `FEATURE_SCHEMA_LINKING` | 否 | 是否启用 Schema Linking，默认 `false` |
| `FEATURE_INDICATOR_RAG` | 否 | 指标 RAG 预留开关，默认 `false` |
| `LLM_MAX_TOKENS` | 否 | LLM 最大输出 Token，默认 `4000` |
| `DB_CONNECT_TIMEOUT` | 否 | MySQL 连接超时，单位秒 |
| `DB_READ_TIMEOUT` | 否 | MySQL 读超时，单位秒 |
| `DB_WRITE_TIMEOUT` | 否 | MySQL 写超时，单位秒 |

## API 使用

除登录和健康检查外，业务接口需要通过 `Authorization` 请求头携带 Token。

### 登录

```bash
curl -X POST http://127.0.0.1:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"user_name":"admin","password":"your-password"}'
```

响应中的 `data.token` 用于后续请求：

```json
{
  "code": 200,
  "message": "登入成功",
  "data": {
    "user_name": "admin",
    "token": "your-token",
    "expires_at": "2026-10-24T12:00:00"
  }
}
```

### 普通查询

```bash
curl -X POST http://127.0.0.1:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"query":"各大区的销售额是多少"}'
```

### 流式查询

```bash
curl -N -X POST http://127.0.0.1:8000/api/v1/query/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"query":"各大区的销售额是多少"}'
```

SSE 事件类型：

- `chunk`：模型生成的 SQL 片段
- `complete_sql`：完整 SQL
- `result`：查询结果
- `error`：执行错误

### Agent 分析报告

```bash
curl -X POST http://127.0.0.1:8000/api/v1/agnet_plan \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"query":"最近三个月利润为什么下降"}'
```

### 接口列表

| 方法 | 路径 | 认证 | 说明 |
| --- | --- | --- | --- |
| `GET` | `/` | 否 | Web 界面 |
| `GET` | `/health` | 否 | 数据库与 LLM 健康检查 |
| `POST` | `/api/v1/login` | 否 | 登录并签发 Token |
| `POST` | `/api/v1/query` | 是 | 非流式问数 |
| `POST` | `/api/v1/query/stream` | 是 | SSE 流式问数 |
| `POST` | `/api/v1/agnet_plan` | 是 | Agent 多步骤分析报告 |

## 安全说明

- 只允许 `SELECT`、`WITH` 等查询语句，并拦截多语句和危险写操作。
- 支持按角色配置行级过滤条件。
- 支持按角色配置敏感字段脱敏。
- 登录密码使用 `bcrypt_sha256` 哈希存储，Token 默认有效期 1 天。
- 当前 CORS 配置为允许所有来源，生产部署前应改为可信域名。
- 生产环境应启用 HTTPS、限制数据库账号权限，并定期清理过期 Token。

## 常见问题

### 登录返回 401

确认 `user` 表中存在对应用户，密码由 `utils.get_hash_password()` 生成，并检查 `role` 值是否符合预期。

### `/health` 返回服务异常

分别检查：

1. MySQL 连接参数是否正确，数据库是否可访问。
2. LLM API Key、地址和模型名称是否有效。
3. 网络或代理是否允许访问外部模型服务。

### 查询时报 Milvus / Embedding 错误

确认 Milvus、Embedding 服务和集合数据已初始化。若暂不使用 RAG，可将 `FEATURE_INDICATOR_KNOWLEDGE` 和 `FEATURE_SCHEMA_LINKING` 设为 `false`。

### 生成 SQL 但执行失败

确认业务表结构与 `json_schema/` 中的定义一致，并检查数据库账号是否具备对应表的查询权限。Agent 模式会将失败 SQL 和数据库错误回传给模型进行有限次数修复重试。

## 开发检查

提交前可执行基础语法检查：

```bash
python -m py_compile \
  agnet_main.py agnet_planner.py api_server.py build_prompt.py config.py \
  join_resolver.py llm_client.py main.py rag_retriever.py \
  runtime_factory.py security.py utils.py
```

## License

当前仓库暂未声明开源许可证。如需对外分发，请补充合适的 License。
