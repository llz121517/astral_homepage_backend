# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# .env 环境变量
ASTRAL_AES_KEY = os.getenv("ASTRAL_AES_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# 启动时验证必要的环境变量
if not ASTRAL_AES_KEY:
    raise RuntimeError("环境变量 ASTRAL_AES_KEY 未设置，请在 .env 文件中配置")
""" # 已迁移入数据库 此次字段仅做初次初始化 一次性用途 故不在此次校验
if not ADMIN_USERNAME:
    raise RuntimeError("环境变量 ADMIN_USERNAME 未设置，请在 .env 文件中配置")
if not ADMIN_PASSWORD:
    raise RuntimeError("环境变量 ADMIN_PASSWORD 未设置，请在 .env 文件中配置")
"""

# ====== 环境开关 ======
ONE_CLICK_PRODUCE = False

# 服务启动配置
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
RELOAD = not ONE_CLICK_PRODUCE
WORKERS = 1 if RELOAD else 4
LOG_LEVEL = "debug" if not ONE_CLICK_PRODUCE else "info"
RELOAD_DIR = ["app", "frontend"]


# FastAPI 基础配置
TITLE = "Astral's Homepage"
VERSION = "0.1.0"
DESCRIPTION = "A simple personal homepage backend."
# 文档开关
DEBUG = not ONE_CLICK_PRODUCE
# None 为关闭文档页
DOCS_URL = "/docs" if DEBUG else None
REDOC_URL = "/redoc" if DEBUG else None
OPENAPI_URL = "/openapi.json" if DEBUG else None


# CORS 跨域配置
# 允许的域名列表 不能为 *
if ONE_CLICK_PRODUCE:
    ALLOW_ORIGINS = ["https://your-domain.com"]
    if ALLOW_ORIGINS == ["https://your-domain.com"] or not ALLOW_ORIGINS:
        raise RuntimeError("ALLOW_ORIGINS 未配置")
else:
    ALLOW_ORIGINS = ["http://localhost:8000"]
# 通用配置 (app.add_middleware)
ALLOW_CREDENTIALS = True
ALLOW_METHODS = ["*"]
ALLOW_HEADERS = ["*"]


# Session / Cookie 配置
SESSION_COOKIE_KEY = "session_id"
SESSION_MAX_AGE = 7 * 24 * 60 * 60  # /天
SESSION_HTTPONLY = True
SESSION_SAMESITE = "lax"   # 允许部分第三方请求携带 Cookie
SESSION_SECURE = ONE_CLICK_PRODUCE   # 启用HTTPS 生产环境设置为 True
SESSION_CLEANUP_AGE = 600  # /s 循环清理过期 Session 的间隔


# 设备状态过滤配置
DEFAULT_DESCRIPTION = "未知应用程序"