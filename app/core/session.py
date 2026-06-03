# app/core/session.py
import uuid
import time
from typing import Dict
from app.config import SESSION_MAX_AGE

# 内存 Session 字典
# 格式：{ session_id: { "user": "...", "expire": 时间 } }
SESSIONS: Dict[str, Dict] = {}
# sid
USER_ACTIVE_SESSION: Dict[str, str] = {}

# 创建 Session
def create_session(user: str = "admin") -> str:
    session_id = str(uuid.uuid4())

    # 同用户已有在线会话 → 删掉旧会话
    if user in USER_ACTIVE_SESSION:
        old_sid = USER_ACTIVE_SESSION[user]
        if old_sid in SESSIONS:
            del SESSIONS[old_sid]

    SESSIONS[session_id] = {
        "user": user,
        "expire": time.time() + SESSION_MAX_AGE
    }
    # 绑定用户最新sid
    USER_ACTIVE_SESSION[user] = session_id
    return session_id

# 校验 Session 是否有效
def verify_session(session_id: str) -> bool:
    if session_id not in SESSIONS:
        return False

    data = SESSIONS[session_id]
    # 删除过期 Session
    if data["expire"] < time.time():
        del SESSIONS[session_id]
        # 同步清用户绑定
        u = data["user"]
        if USER_ACTIVE_SESSION.get(u) == session_id:
            USER_ACTIVE_SESSION.pop(u, None)
        return False

    # 非绑定用户无效
    if USER_ACTIVE_SESSION.get(data["user"], "") != session_id:
        return False

    return True

# 删除 Session（登出）
def delete_session(session_id: str):
    if session_id in SESSIONS:
        del SESSIONS[session_id]