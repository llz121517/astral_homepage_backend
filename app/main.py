# app/main.py
from fastapi import FastAPI, Depends, Request, APIRouter
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from app.core.auth import admin_jump, login_jump
from app.core.session import start_cleanup_worker
from app.core.db.init_db import init_db
from app.config import (
    ALLOW_ORIGINS,
    ALLOW_CREDENTIALS,
    ALLOW_METHODS,
    ALLOW_HEADERS,
    TITLE, VERSION, DESCRIPTION,
    DEBUG, DOCS_URL, REDOC_URL, OPENAPI_URL
)

# 导入 API 路由
from app.api.v1.report import router as report_router
from app.api.v1.status.device import router as device_status_router
from app.api.v1.site.info import router as site_info_router
from app.api.v1.auth import router as auth_router
from app.api.v1.site.theme import router as site_theme_router

app = FastAPI(
    title=TITLE,
    version=VERSION,
    description=DESCRIPTION,
    debug=DEBUG,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=ALLOW_METHODS,
    allow_headers=ALLOW_HEADERS,
)

# 初始化区
init_db()
start_cleanup_worker()

# 中间件

# 异常捕获处理器
async def custom_429(request, exc):
    return JSONResponse(status_code=429,content={"code":0,"msg":"操作频繁，请15分钟后重试"})
app.add_exception_handler(RateLimitExceeded, custom_429)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# 挂载 API 端点
app.include_router(report_router)
app.include_router(device_status_router)
app.include_router(site_info_router)
app.include_router(auth_router)
app.include_router(site_theme_router)


@app.get("/", tags=["page"])
async def index_page():
    # 返回前端入口页面
    return FileResponse("frontend/index.html")

@app.get("/admin", tags=["page"])
async def admin_page(
    request: Request,
    redirect_resp: RedirectResponse = Depends(admin_jump)
):
    if redirect_resp:
        return redirect_resp
    # 返回管理页面
    return FileResponse("frontend/admin/index.html")

@app.get("/login", tags=["page"])
async def login_page(request: Request,
    redirect_resp: RedirectResponse = Depends(login_jump)
):
    if redirect_resp:
        return redirect_resp
    # 登录页面
    return FileResponse("frontend/admin/login.html")