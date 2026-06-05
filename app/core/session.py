# app/core/session.py
import threading
import uuid
import time
import sqlite3
from app.core.db.db import get_cache_conn
from app.config import SESSION_MAX_AGE, SESSION_CLEANUP_AGE


def create_session(user: str) -> str | None:
    """
    创建新会话，自动踢掉该用户的所有旧会话
    """
    sid = str(uuid.uuid4())
    expire = time.time() + SESSION_MAX_AGE
    conn = get_cache_conn()
    cur = conn.cursor()
    try:
        # 踢掉同用户的旧会话
        cur.execute("DELETE FROM sessions WHERE username = ?", (user,))
        # 插入新会话
        cur.execute(
            "INSERT INTO sessions(sid, username, expire_ts) VALUES (?, ?, ?)",
            (sid, user, expire)
        )
        conn.commit()
        return sid
    except sqlite3.Error as e:
        print(f"Session creation failed: {e}")
        return None

def verify_session(session_id: str) -> str | None:
    """
    验证 session_id 是否有效且未过期。
    返回用户名（如有效），否则返回 None。
    """
    if not session_id:
        return None
    now = time.time()
    conn = get_cache_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT username FROM sessions WHERE sid = ? AND expire_ts > ?",
        (session_id, now)
    )
    row = cur.fetchone()
    return row["username"] if row else None


def delete_session(session_id: str):
    """
    删除指定会话（用于登出）
    """
    if not session_id:
        return
    conn = get_cache_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE sid = ?", (session_id,))
    conn.commit()


def cleanup_expired_sessions() -> int | None:
    """
    清理所有已过期的会话，返回删除数量
    """
    now = time.time()
    conn = get_cache_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE expire_ts < ?", (now,))
    deleted = cur.rowcount
    conn.commit()
    return deleted


def start_cleanup_worker():
    """
    启动后台会话清理线程

    创建守护线程定期清理过期的会话记录，主程序退出时自动终止。
    """
    # 定义后台清理工作函数
    def worker():
        while True:
            try:
                deleted = cleanup_expired_sessions()
                if deleted > 0:
                    print(f"Cleaned {deleted} expired sessions.")
            except Exception as e:
                print(f"Session cleanup error: {e}")
            time.sleep(SESSION_CLEANUP_AGE)

    # 创建并启动守护线程
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
