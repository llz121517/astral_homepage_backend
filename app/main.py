# app/main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="Astral's Homepage",
    description="A simple personal homepage backend.",
    version="0.1.0"
)


app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/")
async def serve_frontend():
    # 返回前端入口页面
    return FileResponse("frontend/index.html")