# 使用示例：从零到部署

> **完整演示**: 使用 newstandards 创建一个新项目

---

## 📋 项目需求

创建一个简单的待办事项（Todo）Web 应用：
- 后端：Flask
- 前端：HTML + JavaScript
- 数据库：SQLite
- 部署：Docker + GitHub Actions

---

## Step 1: 修改配置文件（1 分钟）

编辑 `PROJECT-BASE-INFO.md`:

```markdown
# 项目配置（唯一需要修改的文件）

## 基本信息
项目名称: todo-app
项目描述: 简单的待办事项 Web 应用
GitHub 用户名: zhangsan
仓库名称: todo-app

## 部署配置
服务器 IP: 192.168.1.100
SSH 用户名: root
SSH 端口: 22
服务端口: 6100

## 业务需求
创建一个简单的待办事项 Web 应用，支持以下功能：
1. 添加待办事项
2. 标记完成/未完成
3. 删除待办事项
4. 列表展示所有待办事项

技术要求：
- 后端使用 Flask
- 前端使用 HTML + JavaScript
- 数据存储使用 SQLite
- 提供 RESTful API
```

---

## Step 2: 发送 AI Prompt（30 秒）

复制 `AI-PROMPT-SIMPLE.md` 内容，粘贴配置：

```
# 自动生成项目指令

请根据以下配置自动生成完整的 Python 项目（包含代码、测试、CI/CD）：

---CONFIG_START---
# 项目配置（唯一需要修改的文件）

## 基本信息
项目名称: todo-app
项目描述: 简单的待办事项 Web 应用
GitHub 用户名: zhangsan
仓库名称: todo-app

## 部署配置
服务器 IP: 192.168.1.100
SSH 用户名: root
SSH 端口: 22
服务端口: 6100

## 业务需求
创建一个简单的待办事项 Web 应用，支持以下功能：
1. 添加待办事项
2. 标记完成/未完成
3. 删除待办事项
4. 列表展示所有待办事项

技术要求：
- 后端使用 Flask
- 前端使用 HTML + JavaScript
- 数据存储使用 SQLite
- 提供 RESTful API
---CONFIG_END---

## 生成要求
[... AI-PROMPT-SIMPLE.md 的其余内容 ...]

开始生成！
```

---

## Step 3: AI 自动生成项目（5 分钟）

AI 将自动生成以下内容：

### 3.1 项目结构
```
todo-app/
├── .github/workflows/ci.yml
├── src/
│   ├── backend/
│   │   ├── __init__.py
│   │   └── app.py              # Flask 应用
│   ├── core/
│   │   ├── __init__.py
│   │   └── models.py           # 数据模型
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_backend.py
│   └── conftest.py
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .gitattributes
├── pyproject.toml
└── README.md
```

### 3.2 核心代码示例

**src/backend/app.py**:
```python
from flask import Flask, jsonify, request
from src.core.models import Todo, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db.init_app(app)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.json
    todo = Todo(title=data['title'])
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6100)
```

### 3.3 配置文件示例

**pyproject.toml**:
```toml
[project]
name = "todo-app"
version = "0.1.0"
description = "简单的待办事项 Web 应用"
dependencies = ["flask>=3.0.0", "flask-sqlalchemy>=3.0.0"]

[project.optional-dependencies]
dev = ["pytest>=7.4.0", "black>=23.0.0", "ruff>=0.1.0"]
```

**Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir uv
COPY pyproject.toml ./
COPY src/ ./src/
RUN uv sync
EXPOSE 6100
CMD ["uv", "run", "python", "-m", "src.backend.app"]
```

---

## Step 4: 执行创建命令（自动）

AI 提供的命令：

```bash
# 创建项目目录
mkdir todo-app
cd todo-app

# 创建目录结构
mkdir -p src/backend src/core src/utils tests
mkdir -p .github/workflows

# 创建文件（AI 会提供完整内容）
# ... AI 生成的文件内容 ...

# 初始化 Git
git init
git add -A
git commit -m "feat: 初始化待办事项应用"
```

---

## Step 5: 配置 GitHub Secrets（3 分钟）

访问 `https://github.com/zhangsan/todo-app/settings/secrets/actions`

添加以下 Secrets：

| Name | Value |
|------|-------|
| `SSH_HOST` | `192.168.1.100` |
| `SSH_USER` | `root` |
| `SSH_PASSWORD` | `your-password` |
| `SSH_PORT` | `22` |

---

## Step 6: 配置服务器 SSH Key（2 分钟）

```bash
# SSH 登录服务器
ssh root@192.168.1.100

# 生成 SSH Key
ssh-keygen -t ed25519 -C "zhangsan@example.com" -f ~/.ssh/github_deploy

# 查看公钥
cat ~/.ssh/github_deploy.pub

# 复制公钥，添加到 https://github.com/settings/keys

# 测试连接
ssh -T git@github.com
```

---

## Step 7: 推送代码（30 秒）

```bash
# 关联远程仓库
git remote add origin git@github.com:zhangsan/todo-app.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## Step 8: 自动 CI/CD（自动）

GitHub Actions 自动触发：

### CI 阶段（约 3 分钟）
- ✅ 代码格式检查（black）
- ✅ 代码风格检查（ruff）
- ✅ 类型检查（mypy）
- ✅ 运行测试（pytest）

### CD 阶段（约 5 分钟）
- ✅ SSH 连接服务器
- ✅ 拉取最新代码
- ✅ 构建 Docker 镜像
- ✅ 停止旧容器
- ✅ 启动新容器

---

## Step 9: 验证部署（30 秒）

```bash
# 访问应用
curl http://192.168.1.100:6100/health

# 预期输出
{"status": "ok"}

# 测试 API
curl http://192.168.1.100:6100/api/todos

# 预期输出
[]
```

---

## 📊 时间统计

| 步骤 | 时间 | 操作者 |
|------|------|--------|
| 修改配置文件 | 1 分钟 | 开发者 |
| 发送 AI Prompt | 30 秒 | 开发者 |
| AI 生成项目 | 5 分钟 | AI（自动） |
| 执行创建命令 | 自动 | 开发者 |
| 配置 GitHub Secrets | 3 分钟 | 开发者 |
| 配置服务器 SSH Key | 2 分钟 | 开发者 |
| 推送代码 | 30 秒 | 开发者 |
| CI/CD 执行 | 8 分钟 | GitHub（自动） |
| 验证部署 | 30 秒 | 开发者 |

**总时间**: 约 20 分钟  
**人工操作时间**: 约 7 分钟  
**自动化时间**: 约 13 分钟

---

## 🎯 成功标志

- ✅ GitHub Actions 显示绿色 ✓
- ✅ 访问 `http://192.168.1.100:6100/health` 返回 `{"status": "ok"}`
- ✅ 可以添加、查看、删除待办事项

---

## 📚 相关文档

- [PROJECT-BASE-INFO.md](PROJECT-BASE-INFO.md) - 配置文件模板
- [AI-PROMPT-SIMPLE.md](AI-PROMPT-SIMPLE.md) - AI Prompt 模板
- [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - CI/CD 配置指南

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**用途**: 完整使用示例演示
