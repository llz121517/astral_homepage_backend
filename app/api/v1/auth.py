# app/api/v1/auth.py
from fastapi import APIRouter, Request, Response, Form, HTTPException
from app.core.session import create_session, delete_session
from app.config import (
    SESSION_COOKIE_KEY,
    SESSION_MAX_AGE,
    SESSION_HTTPONLY,
    SESSION_SAMESITE,
    SESSION_SECURE,
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# 登录
@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return {"code":2,"msg":"用户名或密码错误"}

    # 创建内存 session
    session_id = create_session(user=username)

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