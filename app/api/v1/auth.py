# app/api/v1/auth.py
from fastapi import APIRouter, Request, Response, Form, Depends
from app.core.auth import admin_required, get_limiter_key
from app.core.crypto import sha256_digest
from app.core.session import create_session, delete_session, verify_session
from app.core.db.db_op import get_account, modify_credential
from app.config import (
    SESSION_COOKIE_KEY,
    SESSION_MAX_AGE,
    SESSION_HTTPONLY,
    SESSION_SAMESITE,
    SESSION_SECURE
)

from slowapi import Limiter

limiter = Limiter(key_func=get_limiter_key)


router = APIRouter(prefix="/api/v1/auth", tags=["auth", "api_v1"])


# 登录
@router.post("/login")
@limiter.limit("5/15minute")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    username = username.strip()
    cfg = get_account()
    pwd = sha256_digest(password)

    # 固定计算量，防止通过响应时间推断用户名是否存在（时序侧信道攻击）
    # 无论用户名是否正确，都同时执行两个比对
    user_match = username == cfg["user"]
    pass_match = pwd == cfg["pwd_hash"]
    if not (user_match and pass_match):
        return {"code":0,"msg":"用户名或密码错误"}

    # 创建 session
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
    return {"code":1,"msg": "已登出"}

@router.get("/check")
async def check_login_status(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and verify_session(session_id):
        return {"code": 1, "msg": "已登录"}
    else:
        return {"code": 1, "msg": "未登录"}


@router.put("/update", dependencies=[Depends(admin_required)])
async def update_credential(
    old_pwd: str | None = Form(None),
    new_username: str | None = Form(None),
    new_pwd: str | None = Form(None)
):
    """
    cfg = get_account()
    if sha256_digest(old_pwd) != cfg["pwd_hash"]:
        return {"code":0,"msg":"原密码不正确"}""" # TODO XXX: 前端尚未适配原密码校验 暂时禁用
    return {"code":0,"msg":"功能禁用"}
    try:
        modify_credential(new_username, new_pwd)
        return {"code":1,"msg":"账号/密码修改成功"}
    except ValueError as e:
        print(e)
        return {"code":0,"msg":"用户名不能为纯空格"}