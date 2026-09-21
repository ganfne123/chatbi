from pydantic import BaseModel,Field
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Any
from collections.abc import Iterator
from main import ChatBiSystem

class QueryRequest(BaseModel):
    """请求类"""
    query:str =Field(...,description="用户问题")


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
        502: {"model": ErrorResponse, "description": "LLM 调用失败"},
        500: {"model": ErrorResponse, "description": "数据库或服务内部异常"},}
    )
def query_chatbi(payload: QueryRequest) ->QuerySuccessResponse:
    print("开始时间"+datetime.now().strftime("%H:%M:%S"))

    result=bi_server.run(payload.query)
    if not result["success"]:
        if result["error_type"] == "validation":
            raise HTTPException(400,detail=result["error"])
        if result["error_type"] == "generate_sql_error":
            raise HTTPException(502,detail=result["error"])
        if result["error_type"] == "database_execute_error":
            raise HTTPException(500,detail=result["error"])
    print("结束时间"+datetime.now().strftime("%H:%M:%S"))
    return QuerySuccessResponse(**result)


@app.post("/api/v1/query/stream")
async def query_chatbi_stream(payload: QueryRequest) -> StreamingResponse:
    print("开始时间"+datetime.now().strftime("%H:%M:%S"))

    def event_generator():
        yield from bi_server.run_stream(payload.query)
    print("结束时间"+datetime.now().strftime("%H:%M:%S"))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
