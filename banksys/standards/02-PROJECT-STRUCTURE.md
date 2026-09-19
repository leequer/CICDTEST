# 项目结构规范（通用 Python 项目）

> **目标**: 建立清晰、可维护、跨平台兼容的项目结构  
> **适用**: Web 应用、数据分析、AI 项目等

---

## 📁 标准目录结构

```
project-root/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD 配置
├── src/
│   ├── __init__.py
│   ├── backend/                # 后端服务（Flask/FastAPI）
│   │   ├── __init__.py
│   │   └── app.py
│   ├── frontend/               # 前端代码（可选）
│   │   ├── __init__.py
│   │   └── static/
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   └── game_logic.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── tests/                      # 测试代码
│   ├── __init__.py
│   ├── test_backend.py
│   └── test_core.py
├── data/                       # 数据文件
│   ├── raw/
│   └── processed/
├── config/                     # 配置文件
│   ├── .env.example
│   └── settings.py
├── docs/                       # 文档
│   ├── API.md
│   └── ARCHITECTURE.md
├── newstandards/               # 项目规范（本目录）
├── .gitignore
├── .gitattributes
├── .dockerignore
├── Dockerfile
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## 📝 目录说明

### 核心目录

#### `src/` - 源代码目录
- **必需**: ✅
- **说明**: 所有 Python 源代码
- **导入方式**: `from src.backend.app import app`

#### `tests/` - 测试目录
- **必需**: ✅
- **说明**: 单元测试、集成测试
- **命名规范**: `test_*.py` 或 `*_test.py`

#### `.github/workflows/` - CI/CD 配置
- **必需**: ✅（使用 GitHub Actions）
- **说明**: 自动化测试和部署配置

### 可选目录

#### `data/` - 数据目录
- **适用**: 数据分析、机器学习项目
- **说明**: 存放数据集、模型文件

#### `config/` - 配置目录
- **适用**: 需要多环境配置的项目
- **说明**: 开发/生产环境配置

#### `docs/` - 文档目录
- **适用**: 需要详细文档的项目
- **说明**: API 文档、架构设计文档

#### `notebooks/` - Jupyter Notebook
- **适用**: 数据分析、探索性分析
- **说明**: 实验性代码、数据可视化

---

## 🔧 配置文件说明

### `pyproject.toml` - 项目配置

```toml
[project]
name = "your-project-name"
version = "0.1.0"
description = "项目描述"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
requires-python = ">=3.11"
dependencies = [
    "flask>=3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

### `.gitignore` - Git 忽略文件

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff
.ruff_cache/

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep
```

### `.gitattributes` - Git 属性配置

```
# 跨平台开发：统一换行符配置
* text=auto

# Python 文件使用 LF
*.py text eol=lf

# Shell 脚本使用 LF
*.sh text eol=lf

# Docker 相关文件使用 LF
Dockerfile text eol=lf
.dockerignore text eol=lf

# YAML 配置文件使用 LF
*.yml text eol=lf
*.yaml text eol=lf

# Markdown 文档使用 LF
*.md text eol=lf

# JSON 配置文件使用 LF
*.json text eol=lf

# 二进制文件不转换
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
```

---

## 🎯 项目类型适配

### Web 应用项目
```
src/
├── backend/          # Flask/FastAPI 后端
├── frontend/         # 前端静态文件
└── utils/            # 工具函数
```

### 数据分析项目
```
src/
├── data/             # 数据处理
├── analysis/         # 分析脚本
├── visualization/    # 可视化
└── utils/            # 工具函数

notebooks/            # Jupyter Notebooks
data/                 # 数据集
```

### AI/机器学习项目
```
src/
├── models/           # 模型定义
├── training/         # 训练脚本
├── inference/        # 推理服务
└── utils/            # 工具函数

data/
├── raw/              # 原始数据
├── processed/        # 处理后数据
└── models/           # 训练好的模型
```

### 游戏项目（如 Match-3）
```
src/
├── backend/          # Flask 后端
│   └── app.py
├── frontend/         # 前端游戏逻辑
│   ├── static/
│   │   ├── js/
│   │   │   └── game.js
│   │   └── css/
│   │       └── style.css
│   └── templates/
│       └── index.html
├── core/             # 游戏核心逻辑
│   └── game_logic.py
└── utils/            # 工具函数
```

---

## 📦 依赖管理

### 使用 uv（推荐）

```bash
# 安装 uv
pip install uv

# 初始化项目
uv init

# 添加依赖
uv add flask

# 添加开发依赖
uv add --dev pytest black ruff mypy

# 安装所有依赖
uv sync

# 安装包含开发依赖
uv sync --extra dev

# 运行命令
uv run python -m src.backend.app
uv run pytest tests/
```

### 使用 pip（传统方式）

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -e .
pip install -e ".[dev]"
```

---

## 🔍 导入规范

### ✅ 正确的导入方式

```python
# 绝对导入（推荐）
from src.backend.app import app
from src.core.game_logic import GameEngine
from src.utils.helpers import format_score

# 相对导入（同一包内）
from .helpers import format_score
from ..core.game_logic import GameEngine
```

### ❌ 错误的导入方式

```python
# 不要使用裸导入
import app  # ❌
from backend.app import app  # ❌

# 不要修改 sys.path
import sys
sys.path.append('..')  # ❌
```

---

## 🚀 启动命令

### 开发环境

```bash
# 使用 uv（推荐）
uv run python -m src.backend.app

# 使用 python
python -m src.backend.app

# 使用 Flask CLI
export FLASK_APP=src.backend.app
flask run --host=0.0.0.0 --port=6100
```

### 生产环境

```bash
# 使用 Docker
docker build -t app:latest .
docker run -p 6100:6100 app:latest

# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:6100 src.backend.app:app
```

---

## ✅ 最佳实践

### 1. 代码组织
- ✅ 按功能模块划分目录
- ✅ 每个模块都有 `__init__.py`
- ✅ 使用绝对导入
- ✅ 避免循环导入

### 2. 配置管理
- ✅ 使用 `.env` 文件管理环境变量
- ✅ 提供 `.env.example` 模板
- ✅ 不要提交敏感信息到 Git

### 3. 测试覆盖
- ✅ 测试目录结构与 src/ 对应
- ✅ 每个模块都有对应测试
- ✅ 使用 pytest fixtures

### 4. 文档维护
- ✅ README.md 包含快速启动指南
- ✅ 代码注释清晰
- ✅ API 文档及时更新

---

## 📚 相关文档

- [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - CI/CD 配置指南
- [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md) - Docker 配置模板
- [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) - 跨平台开发指南

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理
