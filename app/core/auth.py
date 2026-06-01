# app/core/auth.py
from fastapi import Request, HTTPException
from .session import verify_session
from fastapi.responses import RedirectResponse

# 供 /admin 路由 使用的依赖
async def admin_jump(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not verify_session(session_id):
        return RedirectResponse(url="/login", status_code=302)

async def login_jump(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and verify_session(session_id):
        return RedirectResponse(url="/admin", status_code=302)

# 供受保护接口使用的依赖
async def admin_required(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not verify_session(session_id):
        raise HTTPException(status_code=401, detail="未登录")