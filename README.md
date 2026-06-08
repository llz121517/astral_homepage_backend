```
astral_homepage/
├── app/                      # 后端核心代码 (FastAPI)
│   ├── api/v1/               # API 路由模块 (v1 版本)
│   │   ├── site/             # 站点信息相关接口
│   │   │   ├── info.py       # 获取站点基础配置（如标题、简介）
│   │   │   └── theme.py      # 获取主题样式数据
│   │   ├── status/           # 设备状态相关接口
│   │   │   └── device.py     # 获取最新设备上报状态
│   │   ├── auth.py           # 管理员认证接口（登录、登出、检查状态）
│   │   └── report.py         # 设备状态加密上报接口（AES 解密逻辑）
│   ├── core/                 # 核心组件与工具
│   │   ├── db/               # 数据库操作层
│   │   │   ├── db.py         # 数据库连接管理 (SQLite)
│   │   │   ├── db_op.py      # 具体业务 CRUD 操作封装
│   │   │   └── init_db.py    # 数据库初始化脚本（建表、初始数据）
│   │   ├── auth.py           # 页面跳转依赖（登录/管理页权限控制）
│   │   ├── crypto.py         # 密码学工具（AES 解密、SHA256 摘要）
│   │   ├── session.py        # Session 会话管理（创建、验证、清理）
│   │   └── state.py          # 全局状态映射（根据规则匹配设备描述）
│   ├── config.py             # 环境配置与常量定义
│   ├── main.py               # FastAPI 应用入口与路由挂载
│   └── __init__.py
├── data/                     # 数据存储目录
│   ├── db/                   # SQLite 数据库文件存放处
│   │   ├── site.db           # 站点业务库（用户、配置、主题等）
│   │   └── cache.db          # 缓存库（Session、实时设备状态）
│   └── rules.json            # 设备状态描述匹配规则
├── tests/                    # 单元测试目录
│   ├── test_auth.py          # 认证逻辑测试
│   ├── test_db_op.py         # 数据库操作测试
│   ├── test_report.py        # 上报接口测试
│   ├── test_session.py       # 会话管理测试
│   └── test_state.py         # 状态映射测试
├── .env                      # 环境变量配置文件（密钥、账号等）
├── .env.example              # 环境变量示例
├── requirements.txt          # Python 生产环境依赖
├── requirements-dev.txt      # Python 开发环境依赖
└── run.py                    # 项目启动脚本 (Uvicorn)
```