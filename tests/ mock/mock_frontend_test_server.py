# tests/mock_frontend_test_server.py
"""
前端集成测试服务器 - 专门针对 renderSite() 渲染逻辑的 mock

启动：
    python tests/mock_frontend_test_server.py

访问 http://localhost:8000/api/v1/site/info 可查看当前返回的数据。
访问 http://localhost:8000/scenario/basic 切换不同测试场景。
"""
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Mock Site API (Frontend Test)")

# 存储当前使用的场景索引
_current_scenario = 0

# ==========================================
# 测试场景集 - 每个场景针对特定前端逻辑
# ==========================================

SCENARIOS = []

# ---------- 场景 0：完整数据（理想情况）----------
SCENARIOS.append({
    "id": 1,
    "site_title": "Zyyo",
    "keywords": "Python, FastAPI, 前端",
    "description": "个人技术博客",
    "header": "",
    "footer": "",
    "beian": "京ICP备2024xxxxxx号",
    "ico": "/static/img/favicon.ico",
    "avatar_url": "/static/img/avatar.png",
    "avatar_kuang": "/static/img/avatarkuang.png",
    "maxwidth": 1100,
    "title1": "Hello I' m",
    "title2": "Zyyo",
    "tags": ["Python", "FastAPI", "Vue"],
    "timeline": [
        {"title": "项目启动", "date": "2025-01-15"},
        {"title": "完成重构", "date": "2025-06-01"},
    ],
    "descriptions": [
        {"title": "全栈开发者"},
        {"title": "热爱开源"},
    ],
    "side_info": [
        {"title": "年龄:", "content": "24"},
        {"title": "坐标:", "content": "北京"},
    ],
    "switch_indexavatar": 1,
    "switch_leftcard": 1,
    "switch_skill": 1,
    "switch_tcs": 1,
    "active_theme_id": 1,
    "copyright_year": "2024",
    "copyright_name": "Zyyo",
    "icp_number": "京ICP备2024xxxxxx号",
    "icp_link": "https://beian.miit.gov.cn/",
    "updated_at": "2026-06-06 04:54:18",
})

# ---------- 场景 1：测试 parseSpecialText ----------
SCENARIOS.append(SCENARIOS[0].copy() | {
    "descriptions": [
        {"title": "我是一名 [全栈开发者]"},
        {"title": "擅长 {Python} 和 {FastAPI}"},
        {"title": "有 [3年] 的 {后端开发} 经验"},
    ],
})

# ---------- 场景 2：测试空列表 / None ----------
SCENARIOS.append(SCENARIOS[0].copy() | {
    "tags": [],
    "timeline": [],
    "descriptions": [],
    "side_info": [],
})

# ---------- 场景 3：测试全部开关关闭 ----------
SCENARIOS.append(SCENARIOS[0].copy() | {
    "switch_indexavatar": 0,
    "switch_leftcard": 0,
    "switch_skill": 0,
    "switch_tcs": 0,
})

# ---------- 场景 4：测试缺少备案字段 ----------
SCENARIOS.append(SCENARIOS[0].copy() | {
    # 主动删除备案相关字段，测试前端 fallback
    "copyright_year": None,
    "copyright_name": None,
    "icp_number": None,
    "icp_link": None,
})

# ---------- 场景 5：测试 header/footer 注入 ----------
SCENARIOS.append(SCENARIOS[0].copy() | {
    "header": """
        <meta name="custom-meta" content="测试自定义header">
        <script>
            console.log('%c[Header注入] 自定义脚本已执行', 'color: green; font-size: 14px;');
        </script>
    """,
    "footer": """
        <div style="text-align:center;color:#888;margin-top:20px;">
            Powered by <strong>Mock Server</strong>
        </div>
        <script>
            console.log('%c[Footer注入] 自定义脚本已执行', 'color: blue; font-size: 14px;');
        </script>
    """,
})

# ---------- 场景 6：测试超大 maxwidth ----------
SCENARIOS.append(SCENARIOS[0].copy() | {
    "maxwidth": 2000,
})

# ---------- 场景 7：测试 timeline 缺 date ----------
SCENARIOS.append(SCENARIOS[0].copy() | {
    "timeline": [
        {"title": "只有标题，没有日期"},
        {"title": "事件2", "date": "2025-03-15"},
        {"title": ""},
    ],
})

# ---------- 场景 8：随机数据（压力场景）----------
SCENARIOS.append(None)  # 占位，运行时动态生成
_SCENARIO_NAMES = [
    "完整数据（理想情况）",
    "parseSpecialText 渲染",
    "空列表/None",
    "全部开关关闭",
    "缺少备案字段",
    "header/footer 注入",
    "超大 maxwidth",
    "timeline 缺 date",
    "随机数据（压力场景）",
]


def generate_random_scenario():
    """生成随机场景，覆盖各种边界"""
    def rand_bool():
        return random.choice([0, 1])

    def rand_tags():
        counts = random.randint(0, 6)
        pool = ["Python", "FastAPI", "Vue", "Go", "Docker", "K8s", "Redis", "MySQL", "Linux", "Git"]
        return random.sample(pool, min(counts, len(pool)))

    def rand_timeline():
        counts = random.randint(0, 5)
        items = []
        for i in range(counts):
            items.append({
                "title": random.choice(["项目启动", "完成重构", "发布上线", "Bug修复", "功能更新", ""]),
                "date": random.choice([f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}", ""]),
            })
        return items

    def rand_descriptions():
        titles = [
            "我是一名 [全栈开发者]",
            "擅长 {Python} 和 {FastAPI}",
            "热爱 [开源] 和 {分享}",
            "持续学习中",
            "",
        ]
        return [{"title": t} for t in random.sample(titles, random.randint(0, len(titles)))]

    def rand_side_info():
        counts = random.randint(0, 4)
        items = []
        for i in range(counts):
            items.append({
                "title": random.choice(["年龄:", "坐标:", "职业:", "爱好:", "邮箱:"]),
                "content": random.choice(["24", "北京", "后端开发", "编程", "hello@zyyo.net", ""]),
            })
        return items

    scenario = SCENARIOS[0].copy()
    scenario.update({
        "site_title": random.choice(["Zyyo", "Astral Blog", "My Site", ""]),
        "keywords": random.choice(["Python, FastAPI", "tech, blog", ""]),
        "description": random.choice(["个人博客", "技术分享", ""]),
        "maxwidth": random.choice([800, 900, 1000, 1100, 1200, 1400, 1600]),
        "title1": random.choice(["Hello I'm", "你好，我是", "Hi, I am"]),
        "title2": random.choice(["Zyyo", "Astral", "Developer", ""]),
        "tags": rand_tags(),
        "timeline": rand_timeline(),
        "descriptions": rand_descriptions(),
        "side_info": rand_side_info(),
        "switch_indexavatar": rand_bool(),
        "switch_leftcard": rand_bool(),
        "switch_skill": rand_bool(),
        "switch_tcs": rand_bool(),
        "active_theme_id": random.randint(1, 3),
        "copyright_year": random.choice(["2024", "2025", "2026", None]),
        "copyright_name": random.choice(["Zyyo", "Astral", None]),
        "icp_number": random.choice(["京ICP备2024xxxxxx号", ""]),
        "icp_link": "https://beian.miit.gov.cn/",
        "updated_at": (datetime.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )).strftime("%Y-%m-%d %H:%M:%S"),
    })
    return scenario


# ---------- 挂载页面 ----------
# 挂载静态文件
app.mount("/static", StaticFiles(directory="../../frontend/static"), name="static")

@app.get("/")
async def index():
    return FileResponse("../../frontend/index.html")


# ==========================================
# Mock 接口
# ==========================================

@app.get("/api/v1/site/info")
async def mock_get_site_info():
    global _current_scenario
    if _current_scenario == 8:
        data = generate_random_scenario()
    else:
        data = SCENARIOS[_current_scenario]
    return {"code": 1, "msg": "success", "data": data}


@app.get("/api/v1/site/theme")
async def mock_get_theme(theme_id: int = Query(1)):
    """返回模拟的主题 CSS，避免前端 theme 请求失败"""
    themes = {
        1: "/* 默认主题 - 无额外样式 */",
        2: """html {
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
        3: ".gradientText { background: linear-gradient(90deg, #ff6b6b, #4ecdc4); }",
    }
    return {
        "code": 1,
        "msg": "success",
        "data": {
            "id": theme_id,
            "name": f"主题{theme_id}",
            "raw_css": themes.get(theme_id, themes[1]),
        },
    }


# ==========================================
# 场景切换 API
# ==========================================

@app.get("/scenarios")
async def list_scenarios():
    """列出所有可用场景"""
    return {
        "code": 1,
        "data": [
            {"index": i, "name": name}
            for i, name in enumerate(_SCENARIO_NAMES)
        ],
    }


@app.get("/scenario/{index}")
async def switch_scenario(index: int):
    """切换到指定场景"""
    global _current_scenario
    if index < 0 or index >= len(SCENARIOS):
        return {"code": 0, "msg": f"场景索引超出范围 (0~{len(SCENARIOS)-1})"}
    _current_scenario = index
    return {
        "code": 1,
        "msg": f"已切换到场景 [{index}] {_SCENARIO_NAMES[index]}",
        "current_scenario": _current_scenario,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("前端集成测试 Mock 服务器")
    print("=" * 60)
    print("\n可用场景：")
    for i, name in enumerate(_SCENARIO_NAMES):
        print(f"  [{i}] {name}")
    print(f"\n切换场景：")
    print(f"  http://localhost:8000/scenario/{'{index}'}")
    print(f"  http://localhost:8000/scenarios  (查看所有场景)")
    print(f"\n查看当前数据：")
    print(f"  http://localhost:8000/api/v1/site/info")
    print(f"\n默认场景 [0] 已激活，按 Ctrl+C 退出")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
