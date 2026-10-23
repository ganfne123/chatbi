"""pastAPI服务"""
from security import UserContext


from pydantic import BaseModel,Field
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Any
from pathlib import Path
from utils import authenticate_user, create_token,verify_token
from main import ChatBiSystem
from agnet_main import PlanAndExecuteAgnet


class FastAPIRequest(BaseModel):
    code: int
    message: str
    data: Any
class QueryRequest(BaseModel):
    """请求类"""
    query: str = Field(..., min_length=1, description="业务人员的自然语言问题")
    use_few_shot: bool | None = Field(default=None, description="是否启用 Few-shot 示例")
    use_rules: bool | None = Field(default=None, description="是否启用业务规则约束")
    use_guards: bool | None = Field(default=None, description="是否启用错误防护")
    use_schema_linking: bool | None = Field(default=None, description="是否启用 Schema Linking")
    use_indicator: bool | None = Field(default=None, description="是否启用指标 RAG")

class UserLogin(BaseModel):
    """用户登入"""
    user_name: str
    password: str

class LoginResponse(BaseModel):
    user_name: str
    token: str
    expires_at: datetime


class QuerySuccessResponse(BaseModel):
    """查询成功响应。"""

    success: bool = True
    question: str
    sql: str
    columns: list[str]
    formatted: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class HealthSuccessResponse(BaseModel):
    """健康"""

    success: bool = True
    database_health: bool   = True
    llm_health: bool  = True


class ErrorResponse(BaseModel):
    """统一错误响应。"""

    success: bool = False
    error: str
    error_type: str


app=FastAPI()
bi_server=ChatBiSystem()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """统一处理请求体验证错误"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="请求参数校验失败",
            error_type="request_validation",
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """统一处理业务异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=str(exc.detail),
            error_type="http_exception",
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """兜底异常处理，避免把 Python Traceback 直接暴露给前端"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="服务内部异常",
            error_type="internal_server_error",
        ).model_dump(),
    )

@app.get("/health" , response_model=HealthSuccessResponse)
def health_check() -> HealthSuccessResponse:
    database_health=bi_server.database.health_check()
    llm_health=bi_server.llm_client.health_check()
    return HealthSuccessResponse(
        database_health=database_health,
        llm_health=llm_health
        )

@app.post(
    "/api/v1/query",
    response_model=QuerySuccessResponse,
    responses={
        400: {"model": ErrorResponse, "description": "输入问题不合法"},
        401: {"model": ErrorResponse, "description": "用户名或密码错误"},
        502: {"model": ErrorResponse, "description": "LLM 调用失败"},
        500: {"model": ErrorResponse, "description": "数据库或服务内部异常"},}
    )
def query_chatbi(payload: QueryRequest , request:Request) ->QuerySuccessResponse:
    token=request.headers.get("authorization","")
    user_context=verify_token(token)
    result=bi_server.run(payload.query,user_context)
    if not result["success"]:
        if result["error_type"] == "validation":
            raise HTTPException(400,detail=result["error"])
        if result["error_type"] == "generate_sql_error":
            raise HTTPException(502,detail=result["error"])
        if result["error_type"] == "database_execute_error":
            raise HTTPException(500,detail=result["error"])
    return QuerySuccessResponse(**result)



@app.post("/api/v1/agnet_plan")
def agent_plan(payload: QueryRequest ,request: Request):
    token=request.headers.get("authorization"," ")
    user_context=verify_token(token)
    plan_and_execute_agnet=PlanAndExecuteAgnet()
    report=plan_and_execute_agnet.agnet_run(payload.query,user_context)
    return success_response("成功",report)



@app.post("/api/v1/login")
def user_login(user: UserLogin) ->FastAPIRequest:
    account=authenticate_user(user.user_name,user.password)
    if account is None:
        raise HTTPException(
                    status_code=401,
                    detail="用户名或密码错误",
                )
    token,time=create_token(account.username)
    login_response=LoginResponse(
                user_name=account.username,
                token=token,
                expires_at=time,
            )
    return success_response("登入成功",login_response)



@app.post("/api/v1/query/stream")
async def query_chatbi_stream(payload: QueryRequest, request: Request) -> StreamingResponse:
    token=request.headers.get("authorization","")
    user_context=verify_token(token)

    def event_generator():
        yield from bi_server.run_stream(payload.query)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def success_response(message: str , data=None):
    return FastAPIRequest(code=200,message=message,data=data)

# ---------------------- 前端页面（单文件，同源，无需构建） ----------------------
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"

# /static/vendor/*.js 是本地化的 vue / echarts / tailwind，不依赖外网 CDN
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """返回前端单页（登录 + ChatBI 聊天）。"""
    return FileResponse(FRONTEND_INDEX)
