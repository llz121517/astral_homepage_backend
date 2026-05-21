astral_homepage/
├── app/                      # 后端核心代码 (FastAPI)
│   ├── api/v1/               # API 路由模块
│   │   ├── status/           # 设备状态相关接口
│   │   │   └── device.py     # 获取最新设备状态
│   │   ├── user/             # 用户信息接口
│   │   │   └── profile.py    # 获取用户资料（头像、简介）
│   │   └── report.py         # 设备状态上报接口（含 AES 解密逻辑）
│   ├── core/                 # 核心组件
│   │   └── state.py          # 全局状态存储（用于保存设备状态）
│   ├── config.py             # 环境配置与常量定义
│   ├── main.py               # FastAPI 应用入口
│   └── __init__.py
├── frontend/                 # 前端静态资源
│   ├── static/               # 静态文件目录
│   │   ├── css/              # 样式表 (如 bootstrap.min.css)
│   │   ├── js/               # 脚本文件 (main.js)
│   │   ├── user/             # 用户资源 (头像等)
│   │   └── wallpapers/       # 背景壁纸
│   └── index.html            # 单页应用 (SPA) 入口
├── .env                      # 环境变量配置文件
├── .env.example              # 环境变量示例
├── requirements.txt          # Python 依赖列表
├── run.py                    # 项目启动脚本
└── README.md                 # 项目说明文档
