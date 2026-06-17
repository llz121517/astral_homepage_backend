# app/core/init_db.py
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

# 缓存库
CACHE_DB_PATH = DB_DIR / "cache.db"


site_sql_list = [
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
        avatar_url    TEXT NOT NULL DEFAULT '/static/img/avatar.png',
        avatar_kuang  TEXT NOT NULL DEFAULT '/static/img/avatarkuang.png',
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

cache_sql_list = ["""
    CREATE TABLE IF NOT EXISTS sessions(
        sid TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        expire_ts REAL NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_session_expire ON sessions(expire_ts);
    CREATE INDEX IF NOT EXISTS idx_session_user ON sessions(username);
    """,
    """
    CREATE TABLE IF NOT EXISTS device_status (
        device_id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
]

triggers = [
    """
    CREATE TRIGGER IF NOT EXISTS trg_site_config_upd
    AFTER UPDATE ON site_config
    WHEN OLD.updated_at IS NULL OR NEW.updated_at IS NULL OR OLD.updated_at = NEW.updated_at
    BEGIN
        UPDATE site_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_users_upd
    AFTER UPDATE ON users
    WHEN OLD.updated_at IS NULL OR NEW.updated_at IS NULL OR OLD.updated_at = NEW.updated_at
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_themes_upd
    AFTER UPDATE ON themes
    WHEN OLD.updated_at IS NULL OR NEW.updated_at IS NULL OR OLD.updated_at = NEW.updated_at
    BEGIN
        UPDATE themes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_projects_upd
    AFTER UPDATE ON projects
    WHEN OLD.updated_at IS NULL OR NEW.updated_at IS NULL OR OLD.updated_at = NEW.updated_at
    BEGIN
        UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_items_upd
    AFTER UPDATE ON items
    WHEN OLD.updated_at IS NULL OR NEW.updated_at IS NULL OR OLD.updated_at = NEW.updated_at
    BEGIN
        UPDATE items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_icons_upd
    AFTER UPDATE ON icons
    WHEN OLD.updated_at IS NULL OR NEW.updated_at IS NULL OR OLD.updated_at = NEW.updated_at
    BEGIN
        UPDATE icons SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    """,
]

raw_css = """html {
    /*图片模糊背景＋黑色透明卡片+白色svg**/
    --name: 主题5;
    --main_bg_color: url(/static/img/background.jpg);
    --main_text_color: #eeeeee;
    --gradient: linear-gradient(120deg, #bd34fe, #e0321b 30%, #41d1ff 60%);
    --purple_text_color: #747bff;
    --text_bg_color: #00000040;
    --item_bg_color: #00000038;
    --item_hover_color: #33333338;
    --item_left_title_color: #ffffff;
    --item_left_text_color: #ffffff;
    --footer_text_color: #ffffff;
    --left_tag_item: rgb(27 42 57 / 20%);
    --card_filter: 0px;
    --back_filter: 19px;
    --back_filter_color: #00000030;
    --fill:#ffffff;
}""",


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
        for sql in site_sql_list:
            site_conn.executescript(sql)
        # 创建触发器
        for sql in triggers:
            site_conn.executescript(sql)

        # 当 site_config 为空时，插入默认数据
        cur = site_conn.execute("SELECT 1 FROM site_config WHERE id = 1")
        if cur.fetchone() is None:
            site_conn.execute("INSERT INTO site_config DEFAULT VALUES;")

        cur = site_conn.execute("SELECT 1 FROM themes WHERE id = 1")
        if cur.fetchone() is None:
            site_conn.execute("INSERT INTO themes (raw_css) VALUES (?);", raw_css)

        # 仅当 users 无记录时，插入初始管理员账号
        cur = site_conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            if not ADMIN_USERNAME or not ADMIN_PASSWORD:
                raise ValueError("ADMIN_USERNAME or ADMIN_PASSWORD is empty! Please set it in config.")
            hashed_pwd = sha256_digest(ADMIN_PASSWORD)
            site_conn.execute(
                "INSERT INTO users (user, pwd_hash) VALUES (?, ?)",
                (ADMIN_USERNAME.strip(), hashed_pwd)
            )
            print("Temporary credential configuration has been imported from .env into the database!")
            print("SECURITY TIP: You can now remove the temporary credentials from .env!")

    # 初始化多 work 共享缓存库
    with sqlite3.connect(CACHE_DB_PATH) as cache_conn:
        cache_conn.execute("PRAGMA journal_mode=WAL;")
        for sql in cache_sql_list:
            cache_conn.executescript(sql)