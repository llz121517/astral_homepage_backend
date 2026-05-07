# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# .env 环境变量
ASTRAL_AES_KEY = os.getenv("ASTRAL_AES_KEY")

# 启动时验证必要的环境变量
if not ASTRAL_AES_KEY:
    raise RuntimeError("环境变量 ASTRAL_AES_KEY 未设置，请在 .env 文件中配置")


# 服务启动配置
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
RELOAD = True
WORKERS = 1 if RELOAD else 4
LOG_LEVEL = "debug"