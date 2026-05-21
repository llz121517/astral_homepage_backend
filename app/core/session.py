# app/core/session.py
import uuid
import time
from typing import Dict
from app.config import SESSION_MAX_AGE

# 内存 Session 字典
# 格式：{ session_id: { "user": "...", "expire": 时间 } }
SESSIONS: Dict[str, Dict] = {}


# 创建 Session
def create_session(user: str = "admin") -> str:
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "user": user,
        "expire": time.time() + SESSION_MAX_AGE
    }
    return session_id

# 校验 Session 是否有效
def verify_session(session_id: str) -> bool:
    if session_id not in SESSIONS:
        return False

    # 检查是否过期
    if SESSIONS[session_id]["expire"] < time.time():
        del SESSIONS[session_id]
        return False

    return True

# 删除 Session（登出）
def delete_session(session_id: str):
    if session_id in SESSIONS:
        del SESSIONS[session_id]