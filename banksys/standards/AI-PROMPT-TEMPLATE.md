# AI 项目生成 Prompt 模板

> **用途**: 复制此 Prompt 到 AI 对话框，AI 将自动生成完整项目  
> **前提**: 已修改 `PROJECT-CONFIG.md` 配置文件

---

## 🚀 完整 Prompt（复制以下内容）

```
# 项目生成指令

我需要你根据以下配置自动生成一个完整的 Python 项目，包含代码、测试和 CI/CD 配置。

## 项目配置

[在此粘贴 PROJECT-CONFIG.md 的完整内容]

## 生成要求

### 1. 项目结构
按照以下结构创建项目：

```
[项目名称]/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD 配置
├── src/
│   ├── __init__.py
│   ├── backend/                # 后端服务
│   │   ├── __init__.py
│   │   └── app.py              # 主应用入口
│   ├── frontend/               # 前端代码（如需要）
│   │   ├── static/
│   │   │   ├── js/
│   │   │   └── css/
│   │   └── templates/
│   ├── core/                   # 核心业务逻辑
│   │   └── __init__.py
│   └── utils/                  # 工具函数
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_backend.py
│   └── conftest.py
├── newstandards/               # 开发规范（复制模板）
├── .gitignore
├── .gitattributes
├── .dockerignore
├── Dockerfile
├── pyproject.toml
└── README.md
```

### 2. 配置文件要求

#### pyproject.toml
- 项目名称、版本、描述与 PROJECT-CONFIG.md 一致
- Python 版本要求 >=3.11
- 包含开发依赖：pytest, black, ruff, mypy
- 配置 black、ruff、mypy、pytest

#### Dockerfile
- 基于 python:3.11-slim
- 使用清华大学 PyPI 镜像（国内服务器）
- 安装 uv 包管理器
- 正确的 COPY 顺序（pyproject.toml → src/ → uv sync）
- 暴露配置的端口

#### .github/workflows/ci.yml
- CI: 多版本 Python 测试（3.11, 3.12）
- CI: 代码检查（black, ruff, mypy）
- CI: 运行测试（pytest）
- CD: SSH 部署到远程服务器
- CD: Docker 构建和运行
- CD: 超时时间 30 分钟

#### .gitignore
- 排除 Python 缓存、虚拟环境、IDE 配置
- 排除测试覆盖率报告
- 排除环境变量文件

#### .gitattributes
- 统一换行符为 LF
- 确保跨平台兼容

### 3. 代码要求

#### 后端代码 (src/backend/app.py)
- 使用配置的后端框架（Flask/FastAPI）
- 监听配置的端口
- 包含健康检查端点 `/health`
- 根据业务需求生成核心功能

#### 核心业务逻辑 (src/core/)
- 根据业务需求描述生成
- 代码结构清晰、模块化
- 包含必要的错误处理

#### 测试代码 (tests/)
- 使用 pytest 框架
- 测试覆盖率 >= 80%
- 包含单元测试和集成测试

### 4. README.md 要求
- 项目名称和描述
- 快速启动指南
- 本地开发步骤
- CI/CD 说明
- 部署验证方法

### 5. CI/CD 配置要求

#### GitHub Secrets（提醒用户配置）
- SSH_HOST: 服务器 IP
- SSH_USER: SSH 用户名
- SSH_PASSWORD: SSH 密码
- SSH_PORT: SSH 端口

#### 服务器 SSH Key（私有仓库）
- 提醒用户生成 SSH Key
- 提醒用户添加公钥到 GitHub
- 提供配置 ~/.ssh/config 的命令

### 6. 跨平台兼容要求
- 使用 pathlib 处理路径
- 所有文本文件使用 LF 换行符
- 严格匹配文件名大小写

## 执行步骤

请按以下顺序执行：

1. **创建项目结构**
   - 创建所有必需的目录
   - 创建 __init__.py 文件

2. **生成配置文件**
   - pyproject.toml
   - Dockerfile
   - .dockerignore
   - .gitignore
   - .gitattributes
   - .github/workflows/ci.yml

3. **生成核心代码**
   - src/backend/app.py
   - src/core/ 业务逻辑
   - src/utils/ 工具函数

4. **生成测试代码**
   - tests/test_backend.py
   - tests/conftest.py

5. **生成文档**
   - README.md

6. **复制开发规范**
   - 复制 newstandards/ 目录

7. **初始化 Git**
   - git init
   - git add -A
   - git commit -m "feat: 初始化项目"

8. **提供后续步骤**
   - GitHub 仓库创建命令
   - GitHub Secrets 配置提醒
   - 服务器 SSH Key 配置命令
   - 部署验证命令

## 输出格式

请按以下格式输出：

### 步骤 1: 创建项目结构
```bash
# 创建目录的命令
```

### 步骤 2: 配置文件
```python
# 文件路径: pyproject.toml
# 文件内容
```

### 步骤 3: 核心代码
```python
# 文件路径: src/backend/app.py
# 文件内容
```

... 以此类推

### 后续步骤
1. 创建 GitHub 仓库
2. 配置 GitHub Secrets
3. 配置服务器 SSH Key
4. 推送代码触发 CI/CD
5. 验证部署

## 注意事项

- 所有配置必须与 PROJECT-CONFIG.md 一致
- 代码必须符合 Python 最佳实践
- 必须包含完整的错误处理
- 必须支持跨平台开发
- 必须提供详细的注释
- 必须包含类型提示（type hints）

开始生成项目！
```

---

## 📝 使用步骤

### Step 1: 修改配置文件
编辑 `PROJECT-CONFIG.md`，替换所有 `[...]` 中的内容

### Step 2: 复制 Prompt
1. 复制上面的完整 Prompt
2. 将 `[在此粘贴 PROJECT-CONFIG.md 的完整内容]` 替换为实际的配置内容

### Step 3: 发送给 AI
将完整的 Prompt 发送给 AI（如 Trae、Claude、ChatGPT）

### Step 4: 执行 AI 生成的命令
按照 AI 的输出执行命令，创建项目

### Step 5: 配置 CI/CD
按照 AI 提供的后续步骤配置 GitHub Secrets 和服务器 SSH Key

### Step 6: 推送代码
```bash
git remote add origin git@github.com:username/repo.git
git push -u origin main
```

### Step 7: 验证部署
访问 `http://<服务器IP>:<端口>` 验证服务运行

---

## 🎯 配置替换说明

### 必须替换的配置项

| 配置项 | 位置 | 示例 |
|--------|------|------|
| 项目名称 | PROJECT-CONFIG.md | `my-project` |
| 项目描述 | PROJECT-CONFIG.md | `一个简单的 Web 应用` |
| 业务需求 | PROJECT-CONFIG.md | `详细的需求描述` |
| GitHub 用户名 | PROJECT-CONFIG.md | `your-username` |
| 仓库名称 | PROJECT-CONFIG.md | `your-repo` |
| 服务器 IP | PROJECT-CONFIG.md | `192.168.1.100` |
| SSH 用户名 | PROJECT-CONFIG.md | `root` |
| 端口号 | PROJECT-CONFIG.md | `6100` |

### 可选替换的配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| Python 版本 | 3.11 | 可改为 3.12 |
| 后端框架 | Flask | 可改为 FastAPI |
| 数据库 | 无 | 可添加 SQLite/PostgreSQL |
| 测试覆盖率 | 80% | 可调整 |

---

## 🔄 自动化流程

```
修改 PROJECT-CONFIG.md
        ↓
复制 AI Prompt
        ↓
发送给 AI
        ↓
AI 生成完整项目
        ↓
执行创建命令
        ↓
配置 GitHub Secrets
        ↓
配置服务器 SSH Key
        ↓
推送代码
        ↓
自动 CI/CD
        ↓
部署完成
```

---

## 📚 相关文档

- [PROJECT-CONFIG.md](PROJECT-CONFIG.md) - 项目配置文件
- [00-QUICK-START.md](00-QUICK-START.md) - 快速启动指南
- [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - CI/CD 配置指南

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**用途**: AI 驱动的项目自动生成 Prompt
