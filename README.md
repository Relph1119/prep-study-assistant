# 备考学习助手

备考学习助手是一款面向考生的智能学习工具，借鉴多邻国与考试宝的成功经验，以"导入资料—生成题库—智能复习—周期巩固"为闭环，帮助用户高效通过考试。系统支持Word/PDF一键导入，自动拆分章节并提炼知识点；基于大模型即时生成单选、填空、判断等题型，题目与知识点精准对应。用户答题后，评分系统实时给出正误、得分与综合评价，并依据遗忘曲线生成每日任务与周期性回顾，形成个性化复习节奏。技术架构上，系统侧由题库生成、评分与任务调度三大引擎驱动；用户侧提供权限、资料与答题三大模块，前后端分离，接口统一，支持多端同步。

**功能列表：**  
- 系统侧：
  1. 生成题库系统：生成学习章节、生成知识点、生成题目
  2. 评分系统：正错判断、答题得分、综合评分、综合评价
  3. 生成任务系统：生成每日学习、生成每日题目

- 用户侧：  
  1. 权限管理：用户登录、用户注册、用户注销、用户管理
  2. 学习资料管理：学习资料导入、学习资料删除、学习资料查看
  3. 用户答题系统：题目渲染、答题交互

## 🚀 快速开始

### 环境安装

1. 基础环境：Python3.12+

2. 安装UV
```shell
pip install uv
set UV_INDEX=https://mirrors.aliyun.com/pypi/simple
```

3. 安装Python依赖包
```shell
uv sync --python 3.12 --all-extras
```

4. 切换到本地环境(.venv)
```shell
# macOS/Linux
source .venv/bin/activate

# Windows
cd .venv/Scripts
activate
```

### 运行服务

```shell
# 启动 FastAPI 服务
python -m app.main
```

服务启动后，访问以下地址：
- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 交互式文档：http://localhost:8000/redoc

## 📝 接口文档

### 生成题目接口

**接口地址：** `POST /api/v1/questions/generate`

**接口描述：** 根据知识点生成选择题

**请求参数：**
```json
{
  "knowledge_points": ["Python基础语法", "数据类型"]
}
```

**响应示例：**
```json
{
  "success": true,
  "message": "成功为 2 个知识点生成题目",
  "data": [
    {
      "question": "Python是什么类型的语言？",
      "options": [
        {"label": "A", "content": "编译型语言"},
        {"label": "B", "content": "解释型语言"},
        {"label": "C", "content": "汇编语言"},
        {"label": "D", "content": "机器语言"}
      ],
      "correct_answer": "B",
      "explanation": "Python是一种解释型语言，代码在运行时由解释器逐行执行。",
      "knowledge_point": "Python基础语法"
    },
    {
      "question": "Python中下列哪个是不可变数据类型？",
      "options": [
        {"label": "A", "content": "列表"},
        {"label": "B", "content": "字典"},
        {"label": "C", "content": "元组"},
        {"label": "D", "content": "集合"}
      ],
      "correct_answer": "C",
      "explanation": "元组是不可变数据类型，一旦创建就不能修改其内容。",
      "knowledge_point": "数据类型"
    }
  ]
}
```

**参数说明：**
- `knowledge_points`：知识点列表，支持1-10个知识点
- 返回为每个知识点生成的一道选择题
- 题目包含4个选项（A、B、C、D）、正确答案和详细解析

## 🧪 运行测试

```shell
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_question_api.py

# 运行测试并显示覆盖率
pytest tests/ -v --cov=app
```

**测试覆盖范围：**
- 正常请求返回 200
- 返回字段完整且结构正确
- 输入为空时返回 422
- 知识点数量超限时返回 422
- 包含空字符串知识点时返回 422
- 单个知识点生成题目
- 未知知识点生成通用题目
- 响应结构完整性验证

## 🏗️ 项目结构

```
prep-study-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── question.py     # 接口层
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── question.py         # Schema 层
│   ├── services/
│   │   ├── __init__.py
│   │   └── question_service.py # Service 层
│   └── core/
│       ├── __init__.py
│       └── llm.py             # LLM Mock 层
│
├── api/                      # 原有API目录（保留）
│   ├── __init__.py
│   ├── constants.py
│   ├── pprs_server.py
│   ├── settings.py
│   ├── apps/
│   └── utils/
│
├── tests/
│   └── test_question_api.py    # 单元测试
│
├── conf/                     # 配置文件
│   ├── public.pem
│   └── service_conf.yaml
│
├── docker/                   # Docker配置
│   ├── docker-compose-base.yml
│   └── init.sql
│
├── web/                      # 前端目录
│   └── .gitkeep
│
├── .gitignore
├── .python-version
├── pyproject.toml              # 项目配置
├── uv.lock
└── README.md                  # 项目说明
```

## 🛠️ 技术栈

- **Python 3.12**：主要编程语言
- **FastAPI**：Web 框架，提供高性能 API 服务
- **Pydantic**：数据验证和序列化
- **pytest**：测试框架
- **uv**：依赖管理工具
- **Mock LLM**：模拟硅基流动 LLM 返回结构化题目数据

## 📋 开发规范

- 采用分层架构：API层 → Service层 → LLM层
- 使用 Pydantic 进行数据验证
- 所有接口包含完整的单元测试
- 遵循 PEP 8 代码规范
- 使用中文注释和文档

## 🔄 后续计划

- [ ] 集成真实的硅基流动 LLM API
- [ ] 添加更多题型支持（填空题、判断题等）
- [ ] 实现用户系统和权限管理
- [ ] 添加题目难度分级
- [ ] 支持批量题目生成
