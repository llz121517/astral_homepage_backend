# app/api/v1/auth.py
from fastapi import APIRouter, Request, Response, Form, HTTPException
from app.core.session import create_session, verify_session, delete_session
from fastapi.responses import RedirectResponse
from app.config import (
    SESSION_COOKIE_KEY,
    SESSION_MAX_AGE,
    SESSION_HTTPONLY,
    SESSION_SAMESITE,
    SESSION_SECURE,
    ADMIN_PASSWORD
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
"""
# 供 /admin 路由 使用的依赖
async def admin_jump(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not verify_session(session_id):
        return RedirectResponse(url="/login", status_code=302)

async def login_jump(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id or verify_session(session_id):
        return RedirectResponse(url="/admin", status_code=302)

# 供受保护接口使用的依赖
async def admin_required(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not verify_session(session_id):
        raise HTTPException(status_code=401, detail="未登录")
"""

# 登录
@router.post("/login")
async def login(
    response: Response,
    password: str = Form(...)
):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="密码错误")

    # 创建内存 session
    session_id = create_session(user="admin")

    # 设置 HTTP-only Cookie
    response.set_cookie(
        key=SESSION_COOKIE_KEY,
        value=session_id,
        httponly=SESSION_HTTPONLY,
        max_age=SESSION_MAX_AGE,   # 过期时间 /s
        samesite=SESSION_SAMESITE, # 允许部分第三方请求携带 Cookie
        secure=SESSION_SECURE
    )
    return {"code":1,"msg":"登录成功"}

# 登出
@router.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)
    response.delete_cookie(key="session_id")
    return {"msg": "已登出"}