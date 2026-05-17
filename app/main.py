# app/main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# 导入 API 路由
from app.api.v1.report import router as report_router
from app.api.v1.status.device import router as device_status_router
from app.api.v1.user.profile import router as profile_user_router

app = FastAPI(
    title="Astral's Homepage",
    description="A simple personal homepage backend.",
    version="0.1.0"
)


app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

app.include_router(report_router)
app.include_router(device_status_router)
app.include_router(profile_user_router)

@app.get("/")
async def serve_frontend():
    # 返回前端入口页面
    return FileResponse("frontend/index.html")