# app/main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.site import create_site_info
from app.config import (
    ALLOW_ORIGINS,
    ALLOW_CREDENTIALS,
    ALLOW_METHODS,
    ALLOW_HEADERS,
)

# 导入 API 路由
from app.api.v1.report import router as report_router
from app.api.v1.status.device import router as device_status_router
from app.api.v1.site.info import router as site_info_router
from app.api.v1.auth import router as auth_router
from app.config import (
    TITLE, VERSION, DESCRIPTION,
    DEBUG, DOCS_URL, REDOC_URL, OPENAPI_URL
)

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

# 初始化/创建站点信息文件
create_site_info()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# 挂载 API 端点
app.include_router(report_router)
app.include_router(device_status_router)
app.include_router(site_info_router)
app.include_router(auth_router)


@app.get("/")
async def serve_frontend():
    # 返回前端入口页面
    return FileResponse("frontend/index.html")