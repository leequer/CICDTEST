# 🚀 项目快速启动指南（0 到部署 < 30 分钟）

> **适用场景**: 从 Prompt 需求到完整 CI/CD 部署的全流程  
> **支持平台**: Windows / macOS / Linux  
> **部署方式**: Docker + GitHub Actions

---

## 📋 前置准备清单

### 本地开发环境
- [ ] Python 3.11+ 已安装
- [ ] Git 已安装并配置
- [ ] GitHub 账号已创建
- [ ] 代码编辑器（VS Code / PyCharm）

### 可选工具
- [ ] Docker Desktop（本地测试 Docker 镜像）
- [ ] uv 包管理器（`pip install uv`）

---

## 🎯 三步启动流程

### Step 1: 创建项目（5 分钟）

#### 1.1 从模板创建项目
```bash
# 克隆或复制 newstandards/ 到新项目
mkdir my-new-project
cd my-new-project

# 复制 newstandards/ 内容到项目根目录
cp -r /path/to/newstandards/* .
```

#### 1.2 初始化项目结构
```bash
# 创建标准目录结构
mkdir -p src/backend src/frontend tests data config

# 初始化 Git
git init
git add -A
git commit -m "feat: 初始化项目结构"
```

#### 1.3 配置项目信息
编辑 `pyproject.toml`，修改：
- `name = "your-project-name"`
- `description = "项目描述"`
- `authors`

---

### Step 2: 本地开发（10 分钟）

#### 2.1 安装依赖
```bash
# 安装 uv（如果未安装）
pip install uv

# 安装项目依赖
uv sync --extra dev
```

#### 2.2 编写代码
```python
# src/backend/app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6100)
```

#### 2.3 本地测试
```bash
# 运行代码检查
uv run black --check .
uv run ruff check .

# 运行测试
uv run pytest tests/ -v

# 启动服务
uv run python -m src.backend.app
```

---

### Step 3: CI/CD 部署（15 分钟）

#### 3.1 创建 GitHub 仓库
```bash
# 在 GitHub 创建新仓库（public 或 private）
# 然后关联本地仓库
git remote add origin git@github.com:username/repo.git
git branch -M main
git push -u origin main
```

#### 3.2 配置 CI/CD（详见 [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md)）
1. 配置 GitHub Secrets
2. 配置服务器 SSH Key
3. 推送代码触发自动部署

#### 3.3 验证部署
```bash
# 查看 GitHub Actions 日志
# https://github.com/username/repo/actions

# 访问部署的服务
curl http://<服务器IP>:6100
```

---

## 📚 详细文档索引

| 文档 | 用途 | 优先级 |
|------|------|--------|
| [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) | CI/CD 配置完整指南 | ⭐⭐⭐ 必读 |
| [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md) | 项目目录结构规范 | ⭐⭐⭐ 必读 |
| [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md) | Docker 配置模板 | ⭐⭐⭐ 必读 |
| [04-GITHUB-ACTIONS-TEMPLATE.md](04-GITHUB-ACTIONS-TEMPLATE.md) | CI/CD 配置模板 | ⭐⭐⭐ 必读 |
| [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) | 实战踩坑经验 | ⭐⭐ 推荐 |
| [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) | 跨平台开发指南 | ⭐⭐ 推荐 |
| [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) | 常见问题排查 | ⭐ 参考 |

---

## 🎓 教学演示流程

### 课堂演示建议（30 分钟）

#### 第一部分：需求到代码（10 分钟）
1. 展示 Prompt 需求输入
2. 创建项目结构
3. 编写核心代码
4. 本地测试运行

#### 第二部分：CI 配置（10 分钟）
1. 配置 GitHub Actions
2. 推送代码触发 CI
3. 查看代码检查结果
4. 修复 CI 错误

#### 第三部分：CD 部署（10 分钟）
1. 配置服务器 SSH
2. 配置 GitHub Secrets
3. 推送代码触发部署
4. 验证服务运行

---

## ⚡ 常用命令速查

```bash
# 依赖管理
uv sync --extra dev          # 安装所有依赖
uv add package-name          # 添加新依赖

# 代码检查
uv run black .               # 格式化代码
uv run ruff check .          # 代码风格检查
uv run mypy src/             # 类型检查

# 测试
uv run pytest tests/ -v      # 运行测试
uv run pytest --cov=src/     # 测试覆盖率

# Git 操作
git add -A                   # 暂存所有更改
git commit -m "feat: xxx"    # 提交更改
git push                     # 推送到远程

# Docker 操作
docker build -t app:latest . # 构建镜像
docker run -p 6100:6100 app  # 运行容器
docker ps                    # 查看运行中的容器
docker logs container-name   # 查看容器日志
```

---

## 🔗 相关资源

- **GitHub Actions 文档**: https://docs.github.com/en/actions
- **Docker 文档**: https://docs.docker.com/
- **uv 文档**: https://github.com/astral-sh/uv
- **Flask 文档**: https://flask.palletsprojects.com/

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理
