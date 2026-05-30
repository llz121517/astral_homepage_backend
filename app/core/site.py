# app/core/site.py
import json
import os
from pathlib import Path

# 项目根目录 / data / site.json
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_FILE = DATA_DIR / "site.json"

def create_site_info():
    """
    创建站点信息文件
    """
    # 确保目录存在
    os.makedirs(DATA_DIR, exist_ok=True)

    # 不存在则创建默认配置
    if not DATA_FILE.exists():
        default_data = {
            "site_title": "Astral",
            "name": "example",
            "bio": "This is my personal homepage.",
            "avatar_url": "/static/user/default-avatar.webp"
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)

def get_site_info():
    """
    返回站点信息
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("站点信息文件不存在")
    except json.JSONDecodeError:
        raise ValueError("站点信息文件格式损坏")
    except Exception as e:
        raise e

def update_site_info(data: dict):
    """
    更新站点信息
    """
    try:
        current = get_site_info()
        current.update(data)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
        return current
    except Exception as e:
        raise e