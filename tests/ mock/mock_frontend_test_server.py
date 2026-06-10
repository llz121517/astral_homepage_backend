# tests/mock_frontend_test_server.py
"""
前端集成测试服务器 - 劫持 /api/v1/site/info 接口

返回固定格式但随机内容体的 data，用于验证前端对 API 响应的接入是否完善。

用法：
    python tests/mock_frontend_test_server.py

启动后访问 http://localhost:8000/api/v1/site/info 即可看到随机数据。
"""
import random
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Mock Site API (Frontend Test)")

# ---------- 随机数据生成 ----------

def random_timestamp():
    """生成最近一周内的随机时间戳"""
    now = datetime.now()
    delta = timedelta(days=random.randint(0, 7),
                      hours=random.randint(0, 23),
                      minutes=random.randint(0, 59),
                      seconds=random.randint(0, 59))
    return (now - delta).strftime("%Y-%m-%d %H:%M:%S")

def random_tags():
    counts = random.randint(0, 5)
    pool = ["Python", "FastAPI", "Vue", "前端", "后端", "DevOps", "Docker", "SQLite", "TypeScript", "Go"]
    return random.sample(pool, counts)

def random_timeline():
    counts = random.randint(1, 4)
    items = []
    for i in range(counts):
        items.append({
            "title": f"事件标题{i+1}",
            "content": f"这是第{i+1}个时间线事件的详细描述内容，用于测试前端展示。",
            "date": f"202{i}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        })
    return items

def random_descriptions():
    counts = random.randint(1, 3)
    items = []
    for i in range(counts):
        items.append({
            "title": f"描述区块{i+1}",
            "content": f"这是第{i+1}个描述区块的详细内容，用于测试前端展示效果。"
        })
    return items

def random_side_info():
    counts = random.randint(1, 3)
    items = []
    for i in range(counts):
        items.append({
            "title": f"侧边栏{i+1}",
            "content": f"侧边栏第{i+1}项的内容，用于测试侧边栏渲染。"
        })
    return items

# ---------- 挂载页面 ----------
# 挂载静态文件
app.mount("/static", StaticFiles(directory="../../frontend/static"), name="static")

@app.get("/")
async def index():
    return FileResponse("../../frontend/index.html")

# ---------- Mock 接口 ----------

@app.get("/api/v1/site/info")
async def mock_get_site_info():
    return {
        "code": 1,
        "msg": "success",
        "data": {
            "id": 1,
            "site_title": random.choice(["Zyyo", "Astral Blog", "My Site", "Dev Notes"]),
            "keywords": ", ".join(random_tags()) if random.random() > 0.3 else "",
            "description": random.choice([
                "个人技术博客，记录学习与生活",
                "分享技术、思考和创作",
                "探索编程世界的乐趣",
                "",
            ]),
            "header": random.choice(["欢迎来到我的主页", "Hello World", "Hi there!", ""]),
            "footer": random.choice([
                "© 2026 Zyyo. All rights reserved.",
                "Powered by Astral Homepage",
                "",
            ]),
            "beian": random.choice(["京ICP备2026xxxxxx号", ""]),
            "ico": "/static/img/favicon.ico",
            "avatar_url": "/static/img/avatar.png",
            "avatar_kuang": "/static/img/avatarkuang.png",
            "maxwidth": random.choice([900, 1000, 1100, 1200]),
            "title1": random.choice(["Hello I'm", "你好，我是", "Hi, I am"]),
            "title2": random.choice(["Zyyo", "Astral", "Developer"]),
            "tags": random_tags(),
            "timeline": random_timeline(),
            "descriptions": random_descriptions(),
            "side_info": random_side_info(),
            "switch_indexavatar": random.choice([0, 1]),
            "switch_leftcard": random.choice([0, 1]),
            "switch_skill": random.choice([0, 1]),
            "switch_tcs": random.choice([0, 1]),
            "active_theme_id": random.randint(1, 3),
            "updated_at": random_timestamp(),
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
