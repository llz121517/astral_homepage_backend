# app/core/db.py
"""
数据库连接管理
"""
import threading
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
DB_DIR = ROOT / "data" / "db"
# 主页业务库
SITE_DB_PATH = DB_DIR / "site.db"

# 多 work 共享缓存库
CACHE_DB_PATH = DB_DIR / "cache.db"

# 连接池
_cache_local = threading.local()
_site_local = threading.local()


def get_site_conn() -> sqlite3.Connection:
    if not hasattr(_site_local, "conn"):
        conn = sqlite3.connect(
            str(SITE_DB_PATH),
            check_same_thread=True,
            timeout=10.0
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        _site_local.conn = conn
    return _site_local.conn


def get_cache_conn() -> sqlite3.Connection:
    if not hasattr(_cache_local, "conn"):
        conn = sqlite3.connect(
            str(CACHE_DB_PATH),
            check_same_thread=True,
            timeout=10.0
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        _cache_local.conn = conn
    return _cache_local.conn
