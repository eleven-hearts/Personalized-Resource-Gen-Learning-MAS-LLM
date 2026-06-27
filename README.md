# 远航智学 — 基于大模型的个性化资源生成与学习多智能体系统

> 第十五届中国软件杯大赛 A3 赛题作品 | 出题企业：科大讯飞股份有限公司

## 项目简介

远航智学是一个面向高等教育场景的个性化学习平台，利用讯飞星火大模型驱动多个 AI 智能体协同工作，实现"因材施教"的数字化落地。系统通过对话自动构建学生画像，规划个性化学习路径，生成多模态学习资源，提供智能辅导和效果评估，让每位学生拥有专属的 AI 学习伙伴。

前端采用 Apple 液态玻璃（Glassmorphism）风格设计，融入帆船、灯塔等航海元素，象征知识海洋中的远航探索。

## 核心功能

| 功能 | 说明 |
|------|------|
| 对话式学习画像 | AI 通过自然语言对话自动抽取学生特征，构建动态画像（知识基础、认知风格、学习节奏等） |
| 个性化学习路径 | 上传 PDF 或从资源生成学习路径，多路径管理，可视化时间线 + 灯塔完成动画 |
| 多模态资源生成 | AI 生成讲解文档、思维导图、练习题、拓展阅读、代码案例等 5 种类型资源 |
| 智能辅导对话 | 多轮 AI 对话答疑，支持概念解释、代码示例、Debug 排查三种模式 |
| 测验与错题本 | 每阶段测验评估，错题自动收录，支持"消灭"错题（带动画） |
| 每日打卡砖墙 | 登录即打卡，答题 0-5 题浅绿、6+ 题深绿，连续打卡天数统计 |
| 学习仪表盘 | 总做题数、正确率、路径进度、活跃天数等多维度统计 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Vue 3 (Composition API) + Vite 5 |
| UI 组件 | Element Plus 2.7 |
| 状态管理 | Pinia |
| HTTP 请求 | Axios |
| Markdown 渲染 | marked + highlight.js |
| 后端框架 | Python 3.10 + FastAPI 0.111 |
| ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite（开发） |
| 认证 | JWT (python-jose + passlib/bcrypt) |
| AI 大模型 | 讯飞星火大模型 3.5（WebSocket API） |
| PDF 解析 | PyPDF2 |

## 项目结构

```
Personalized-Resource-Gen-Learning-MAS-LLM/
│
├── backend/                          # 后端 — Python FastAPI
│   ├── main.py                       # 入口：uvicorn 启动服务器
│   ├── requirements.txt              # Python 依赖
│   ├── .env.example                  # 环境变量模板
│   └── app/
│       ├── core/                     # 基础设施层
│       │   ├── config.py             #   全局配置（数据库URL、AI密钥、JWT等）
│       │   ├── database.py           #   数据库连接、会话管理、建表
│       │   └── security.py           #   JWT 生成/验证、密码哈希、认证依赖
│       │
│       ├── models/                   # 数据模型层（SQLAlchemy ORM）
│       │   ├── user.py               #   User 模型（用户表）
│       │   ├── resource.py           #   Resource 模型（学习资源表）
│       │   └── learning.py           #   LearningPath / PathNode / QuizQuestion
│       │                             #   WrongAnswer / DailyCheckIn 模型
│       │
│       ├── schemas/                  # 数据校验层（Pydantic）
│       │   ├── user.py               #   注册/登录/Token Schema
│       │   └── resource.py           #   资源创建/响应 Schema
│       │
│       ├── api/endpoints/            # API 路由层
│       │   ├── auth.py               #   POST /register, /login
│       │   ├── users.py              #   GET/PUT /users/me
│       │   ├── agents.py             #   AI 智能体：生成路径、从资源生成路径
│       │   ├── chat.py               #   AI 对话
│       │   ├── resources.py          #   资源 CRUD + AI 生成
│       │   ├── quiz.py               #   测验、添加资源到节点、删除路径
│       │   ├── dashboard.py          #   统计、错题本、每日打卡、打卡日历
│       │   ├── evaluation.py         #   学习评估
│       │   └── report.py             #   学习报告
│       │
│       ├── agents/                   # AI 多智能体系统（MAS）
│       │   ├── base_agent.py         #   基类：系统提示词 + LLM 调用封装
│       │   ├── coordinator.py        #   协调者：分配请求给子智能体
│       │   ├── profile_agent.py      #   画像智能体：分析学生特征
│       │   ├── path_agent.py         #   路径智能体：规划学习路径
│       │   ├── resource_agent.py     #   资源智能体：生成学习资源
│       │   ├── tutor_agent.py        #   辅导智能体：答疑解惑
│       │   └── evaluation_agent.py   #   评估智能体：评估学习效果
│       │
│       └── services/
│           └── spark_service.py      # 讯飞星火大模型 API 封装（WebSocket）
│
├── frontend/                         # 前端 — Vue 3 + Vite
│   ├── index.html                    # SPA 入口（远航智学标题 + 帆船favicon）
│   ├── package.json                  # 依赖 & 脚本
│   ├── vite.config.js                # Vite 配置（代理 /api → :8000）
│   └── src/
│       ├── main.js                   # Vue 应用入口（挂载、注册ElementPlus）
│       ├── App.vue                   # 根组件（全局CSS变量 + Canvas背景）
│       │
│       ├── api/                      # API 请求层
│       │   ├── request.js            #   Axios 实例（JWT 拦截器、401跳转）
│       │   ├── auth.js               #   登录、注册、获取当前用户
│       │   ├── chat.js               #   发送聊天消息
│       │   ├── resource.js           #   资源列表、生成、删除
│       │   ├── learning.js           #   路径相关：获取/生成/删除路径等
│       │   └── dashboard.js          #   统计、错题、打卡
│       │
│       ├── components/               # 公共组件
│       │   └── LiquidGlassBg.vue     #   全屏 Canvas 液态玻璃背景（光斑+光弧）
│       │
│       ├── composables/              # 可复用逻辑（Composition API）
│       │   └── useLiquidGlass.js     #   卡片 Canvas 鼠标跟随高光
│       │
│       ├── router/
│       │   └── index.js              # 路由配置 + 导航守卫
│       │
│       ├── stores/                   # Pinia 状态管理
│       │   ├── index.js              #   Pinia 实例
│       │   └── user.js               #   用户状态（token、userInfo）
│       │
│       └── views/                    # 页面组件
│           ├── Login.vue             #   登录/注册（玻璃卡片 + 帆船SVG）
│           ├── Layout.vue            #   布局壳（玻璃侧边栏 + 帆船Logo + 波浪）
│           ├── Dashboard.vue         #   仪表盘（统计卡 + 进度 + 打卡砖墙）
│           ├── Chat.vue              #   AI 对话（玻璃消息气泡）
│           ├── Resources.vue         #   学习资源（生成/删除/生成路径）
│           ├── LearningPath.vue      #   学习路径（时间线 + 灯塔 + 删除路径）
│           ├── Profile.vue           #   个人中心 + AI 画像
│           ├── QuizDialog.vue        #   测验弹窗
│           └── WrongAnswerDialog.vue #   错题本（消灭动画）
│
├── data/                             # 示例课程数据
│   └── courses/机器学习基础/
│       ├── 课程大纲.md
│       └── 知识点/
│           ├── 线性回归.md
│           └── 逻辑回归.md
│
├── docs/                             # 项目文档
│   ├── 系统开发说明书.md
│   ├── 测试说明书.md
│   └── 开源声明.md
│
└── .gitignore
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

### 1. 克隆项目

```bash
git clone https://github.com/eleven-hearts/Personalized-Resource-Gen-Learning-MAS-LLM.git
cd Personalized-Resource-Gen-Learning-MAS-LLM
```

### 2. 启动后端

```bash
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# （可选）复制环境变量文件并填写星火大模型密钥
cp .env.example .env

# 启动后端服务
python main.py
```

后端默认运行在 `http://localhost:8000`，API 文档访问 `http://localhost:8000/docs`。

### 3. 启动前端

```bash
# 新开一个终端
cd frontend

# 安装前端依赖
npm install

# 启动开发服务器
npm run dev
```

前端默认运行在 `http://localhost:3000`。

### 4. 访问系统

浏览器打开 `http://localhost:3000`，注册账号后即可使用全部功能。

## 数据库

项目使用 SQLite，数据库文件位于 `backend/data/app.db`。

数据表结构：

| 表名 | 说明 |
|------|------|
| `users` | 用户账号 |
| `resources` | 学习资源（Markdown 内容） |
| `learning_paths` | 学习路径 |
| `path_nodes` | 路径节点（阶段） |
| `quiz_questions` | 测验题目 |
| `wrong_answers` | 错题记录 |
| `daily_check_ins` | 每日打卡记录 |

查看数据的方式：
- **命令行**：`cd backend && python -c "import sqlite3; c=sqlite3.connect('data/app.db'); print(c.execute('SELECT * FROM users').fetchall())"`
- **可视化**：安装 [DB Browser for SQLite](https://sqlitebrowser.org/)，双击打开 `app.db`

## AI 多智能体架构

系统采用多智能体协作（Multi-Agent System）架构，6 个专业智能体各司其职：

```
用户请求
  │
  ▼
CoordinatorAgent（协调者）
  ├── ProfileAgent（画像）→ 分析学生特征，更新学习画像
  ├── PathAgent（路径）  → 规划个性化学习路径
  ├── ResourceAgent（资源）→ 生成讲解/题目/导图等资源
  ├── TutorAgent（辅导）  → 答疑解惑，引导思考
  └── EvaluationAgent（评估）→ 评估学习效果，给出建议
```

所有智能体通过 `spark_service.py` 调用讯飞星火大模型 API，Prompt 以 f-string 形式写在各智能体的 `_build_xxx_prompt()` 方法中。

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录（返回 JWT） |
| GET | `/api/v1/users/me` | 获取当前用户信息 |
| PUT | `/api/v1/users/me` | 更新用户信息 |
| POST | `/api/v1/agents/learning-path` | AI 生成学习路径 |
| POST | `/api/v1/agents/generate-path-from-resource/{id}` | 从资源 AI 生成路径 |
| POST | `/api/v1/chat/` | AI 对话 |
| GET | `/api/v1/resources/` | 获取资源列表 |
| POST | `/api/v1/resources/generate` | AI 生成学习资源 |
| DELETE | `/api/v1/resources/{id}` | 删除资源 |
| GET | `/api/v1/quiz/questions/{node_id}` | 获取节点测验题 |
| POST | `/api/v1/quiz/submit` | 提交测验答案 |
| POST | `/api/v1/quiz/node/{id}/add-resource` | 添加资源到节点 |
| DELETE | `/api/v1/quiz/path/{id}` | 删除学习路径 |
| GET | `/api/v1/dashboard/stats` | 获取仪表盘统计 |
| GET | `/api/v1/dashboard/wrong-answers` | 获取错题本 |
| DELETE | `/api/v1/dashboard/wrong-answers/{id}` | 删除错题 |
| POST | `/api/v1/dashboard/check-in` | 每日打卡 |
| GET | `/api/v1/dashboard/check-in-calendar` | 获取打卡日历 |

## 构建部署

```bash
# 前端生产构建
cd frontend
npm run build
# 产物在 frontend/dist/ 目录

# 后端生产启动（关闭热重载）
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 开源声明

本项目使用了以下开源项目/工具，详见 `docs/开源声明.md`。

## 团队信息

- 赛题：A3 - 基于大模型的个性化资源生成与学习多智能体系统开发
- 出题企业：科大讯飞股份有限公司
