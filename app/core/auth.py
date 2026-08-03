# app/core/auth.py
from fastapi import Request, HTTPException
from .session import verify_session
from fastapi.responses import RedirectResponse


def get_limiter_key(request: Request) -> str:
    """
    自定义限流 key：用 TCP 真实连接 IP + User-Agent 前缀组合。

    原因：slowapi 默认的 get_remote_address 只取 request.client.host，
    若 uvicorn/代理开启了 X-Forwarded-For 信任，攻击者可伪造 IP 绕过限流。
    """
    ip = request.client.host if request.client else "unknown"
    ua_prefix = (request.headers.get("User-Agent", "") or "")[:20]
    return f"{ip}|{ua_prefix}"

class RedirectToLogin(HTTPException):
    """自定义异常，携带重定向目标"""
    def __init__(self, url: str = "/login"):
        super().__init__(status_code=302, headers={"Location": url})

async def admin_jump(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not verify_session(session_id):
        raise RedirectToLogin("/login")

async def login_jump(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and verify_session(session_id):
        raise RedirectToLogin("/admin")

# 受保护接口依赖
async def admin_required(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not verify_session(session_id):
        raise HTTPException(status_code=401, detail="未登录")