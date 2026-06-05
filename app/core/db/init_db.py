# app/core/init_db.py
import threading
import sqlite3
from pathlib import Path
from app.core.crypto import sha256_digest
from app.config import (
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)

ROOT = Path(__file__).parent.parent.parent.parent
DB_DIR = ROOT / "data" / "db"
# 主页业务库
SITE_DB_PATH = DB_DIR / "site.db"

# 会话独立库
SESSION_DB_PATH = DB_DIR / "session.db"


sql_list = [
    # 1. 站点配置
    """
    CREATE TABLE IF NOT EXISTS site_config (
        id            INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
        site_title    TEXT NOT NULL DEFAULT 'Zyyo',
        keywords      TEXT NOT NULL DEFAULT '',
        description   TEXT NOT NULL DEFAULT '',
        header        TEXT NOT NULL DEFAULT '',
        footer        TEXT NOT NULL DEFAULT '',
        beian         TEXT NOT NULL DEFAULT '',
        ico           TEXT NOT NULL DEFAULT '/static/img/favicon.ico',
        avatar_url          TEXT NOT NULL DEFAULT '/static/img/logo.png',
        maxwidth      INTEGER NOT NULL DEFAULT 1100,
        title1        TEXT NOT NULL DEFAULT "Hello I' m",
        title2        TEXT NOT NULL DEFAULT 'Zyyo',
        tags          TEXT NOT NULL DEFAULT '[]',
        timeline      TEXT NOT NULL DEFAULT '[]',
        descriptions  TEXT NOT NULL DEFAULT '[]',
        side_info     TEXT NOT NULL DEFAULT '[]',
        switch_indexavatar  INTEGER NOT NULL DEFAULT 0,
        switch_leftcard   INTEGER NOT NULL DEFAULT 0,
        switch_skill      INTEGER NOT NULL DEFAULT 0,
        switch_tcs        INTEGER NOT NULL DEFAULT 0,
        active_theme_id INTEGER NOT NULL DEFAULT 1,
        updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # 2. 用户表
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user        TEXT NOT NULL,
        pwd_hash    TEXT NOT NULL,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # 3. 主题表
    """
    CREATE TABLE IF NOT EXISTS themes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL DEFAULT '未命名主题',
        raw_css TEXT NOT NULL DEFAULT '',
        weight INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_themes_weight ON themes(weight);
    """,
    #4. 项目分类
    """
    CREATE TABLE IF NOT EXISTS projects (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        icon       TEXT NOT NULL DEFAULT '',
        type       INTEGER NOT NULL DEFAULT 0,
        weight     INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_projects_weight ON projects(weight);
    """,
    #5. 项目详情（外键级联删除）
    """
    CREATE TABLE IF NOT EXISTS items (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        icon       TEXT NOT NULL DEFAULT '',
        des        TEXT NOT NULL DEFAULT '',
        href       TEXT NOT NULL DEFAULT '',
        project_id INTEGER NOT NULL,
        weight     INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_items_weight ON items(weight);
    CREATE INDEX IF NOT EXISTS idx_items_project ON items(project_id);
    """,
    #6. 社交图标
    """
    CREATE TABLE IF NOT EXISTS icons (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        icon       TEXT NOT NULL DEFAULT '',
        href       TEXT NOT NULL DEFAULT '',
        onclick    TEXT NOT NULL DEFAULT '',
        weight     INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_icons_weight ON icons(weight);
    """
]


def init_db() -> None:
    """
    初始化数据库，建文件夹+建表+插入初始管理员凭证（仅当 site_config 为空时）
    """
    # 创建 data/db 文件夹
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # 初始化 site.db（主页业务库）
    with sqlite3.connect(SITE_DB_PATH) as site_conn:
        site_conn.execute("PRAGMA journal_mode=WAL;")
        site_conn.execute("PRAGMA foreign_keys=ON;")

        # 执行所有建表语句
        for sql in sql_list:
            site_conn.executescript(sql)

        # 仅当 site_config 无记录时，插入初始管理员账号
        cur = site_conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            if not ADMIN_USERNAME or not ADMIN_PASSWORD:
                raise ValueError("ADMIN_USERNAME or ADMIN_PASSWORD is empty! Please set it in config.")
            hashed_pwd = sha256_digest(ADMIN_PASSWORD)
            site_conn.execute(
                "INSERT INTO users (user, pwd_hash) VALUES (?, ?)",
                (ADMIN_USERNAME, hashed_pwd)
            )
            print("Temporary credential configuration has been imported from .env into the database!")
            print("SECURITY TIP: You can now remove the temporary credentials from .env!")

    # 初始化独立会话库 session.db
    with sqlite3.connect(SESSION_DB_PATH) as sess_conn:
        sess_conn.execute("PRAGMA journal_mode=WAL;")
        sess_conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions(
                sid TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expire_ts REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_session_expire ON sessions(expire_ts);
            CREATE INDEX IF NOT EXISTS idx_session_user ON sessions(username);
        """)