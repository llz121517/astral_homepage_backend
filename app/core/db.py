# app/core/db.py
from pathlib import Path
import threading
import sqlite3

ROOT = Path(__file__).parent.parent.parent
DB_DIR = ROOT / "data" / "db"
# 主页业务库
SITE_DB_PATH = DB_DIR / "site.db"

# 会话独立库
SESSION_DB_PATH = DB_DIR / "session.db"

# 连接池
_session_local = threading.local()
_site_local = threading.local()

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
        logo          TEXT NOT NULL DEFAULT '/static/img/logo.png',
        maxwidth      INTEGER NOT NULL DEFAULT 1100,
        title1        TEXT NOT NULL DEFAULT "Hello I' m",
        title2        TEXT NOT NULL DEFAULT 'Zyyo',
        tags          TEXT NOT NULL DEFAULT '[]',
        timeline      TEXT NOT NULL DEFAULT '[]',
        descriptions  TEXT NOT NULL DEFAULT '[]',
        side_info     TEXT NOT NULL DEFAULT '[]',
        switch_indexlogo  INTEGER NOT NULL DEFAULT 0,
        switch_leftzyyo   INTEGER NOT NULL DEFAULT 0,
        switch_skill      INTEGER NOT NULL DEFAULT 0,
        switch_tcs        INTEGER NOT NULL DEFAULT 0,
        active_theme_id INTEGER NOT NULL DEFAULT 1,
        user            TEXT NOT NULL DEFAULT 'admin',
        pwd             TEXT NOT NULL DEFAULT '',
        avatar_url      TEXT NOT NULL DEFAULT '/static/user/default-avatar.webp',
        bio             TEXT NOT NULL DEFAULT '',
        site_name       TEXT NOT NULL DEFAULT 'Astral',
        updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    # 2. 主题表
    """
    CREATE TABLE IF NOT EXISTS themes (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        name                 TEXT NOT NULL DEFAULT '未命名主题',
        main_bg_color        TEXT NOT NULL DEFAULT '',
        main_text_color      TEXT NOT NULL DEFAULT '#eeeeee',
        gradient             TEXT NOT NULL DEFAULT '',
        purple_text_color    TEXT NOT NULL DEFAULT '#747bff',
        text_bg_color        TEXT NOT NULL DEFAULT '#00000040',
        item_bg_color        TEXT NOT NULL DEFAULT '#00000038',
        item_hover_color     TEXT NOT NULL DEFAULT '#33333338',
        item_left_title_color TEXT NOT NULL DEFAULT '#ffffff',
        item_left_text_color TEXT NOT NULL DEFAULT '#ffffff',
        footer_text_color    TEXT NOT NULL DEFAULT '#ffffff',
        left_tag_item        TEXT NOT NULL DEFAULT 'rgb(27 42 57 / 20%)',
        card_filter          TEXT NOT NULL DEFAULT '0px',
        back_filter          TEXT NOT NULL DEFAULT '39px',
        back_filter_color    TEXT NOT NULL DEFAULT '#00000030',
        fill                 TEXT NOT NULL DEFAULT '#ffffff',
        weight               INTEGER NOT NULL DEFAULT 0,
        created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_themes_weight ON themes(weight);
    """,
    #3. 项目分类
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
    #4. 项目详情（外键级联删除）
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
    #5. 社交图标
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


def init_db():
    """
    初始化数据库，建文件夹+建表
    """
    # 创建data/db文件夹
    DB_DIR.mkdir(exist_ok=True)
    with sqlite3.connect(SITE_DB_PATH) as site_conn:
        site_conn.execute("PRAGMA journal_mode=WAL;")
        site_conn.execute("PRAGMA foreign_keys=ON;")
        for sql in sql_list:
            site_conn.executescript(sql)

    # 初始化独立会话库
    with sqlite3.connect(SESSION_DB_PATH) as sess_conn:
        sess_conn.execute("PRAGMA journal_mode=WAL;")
        sess_conn.executescript("""
            CREATE TABLE IF NOT EXISTS admin_session(
                sid TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expire_ts REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_session_expire ON admin_session(expire_ts);
            CREATE INDEX IF NOT EXISTS idx_session_user ON admin_session(username);
        """)


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


def get_session_conn() -> sqlite3.Connection:
    if not hasattr(_session_local, "conn"):
        conn = sqlite3.connect(
            str(SESSION_DB_PATH),
            check_same_thread=True,
            timeout=10.0
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        _session_local.conn = conn
    return _session_local.conn
