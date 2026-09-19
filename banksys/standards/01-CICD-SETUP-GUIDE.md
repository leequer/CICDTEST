# CI/CD 配置完整指南（GitHub Actions + Docker）

> **目标**: 实现从代码提交到自动部署的完整闭环  
> **部署方式**: Docker 容器化部署  
> **适用场景**: 私有/公开仓库均可

---

## 📋 配置清单总览

| 步骤 | 配置项 | 位置 | 必需 |
|------|--------|------|------|
| 1 | GitHub 仓库创建 | GitHub 网站 | ✅ |
| 2 | 服务器 SSH Key | 服务器 + GitHub | ✅ |
| 3 | GitHub Secrets | 仓库 Settings | ✅ |
| 4 | Dockerfile | 项目根目录 | ✅ |
| 5 | .dockerignore | 项目根目录 | ✅ |
| 6 | .github/workflows/ci.yml | 项目根目录 | ✅ |
| 7 | .gitattributes | 项目根目录 | ⭐ 推荐 |

---

## 🔧 详细配置步骤

### Step 1: 创建 GitHub 仓库

#### 1.1 在 GitHub 创建仓库
1. 访问 https://github.com/new
2. 填写仓库名称（如 `my-project`）
3. 选择 Public 或 Private
4. **不要**勾选 "Add a README file"
5. 点击 "Create repository"

#### 1.2 关联本地仓库
```bash
# 在项目根目录执行
git remote add origin git@github.com:username/repo.git
git branch -M main
git push -u origin main
```

---

### Step 2: 配置服务器 SSH Key（私有仓库必需）

#### 2.1 生成 SSH Key（在服务器上执行）
```bash
# SSH 登录到服务器
ssh user@server-ip

# 生成 SSH Key
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/github_deploy

# 查看公钥
cat ~/.ssh/github_deploy.pub
```

#### 2.2 添加 SSH Key 到 GitHub
1. 复制公钥内容（`github_deploy.pub`）
2. 访问 https://github.com/settings/keys
3. 点击 "New SSH key"
4. Title: `Server Deploy Key`
5. Key: 粘贴公钥内容
6. 点击 "Add SSH key"

#### 2.3 配置 SSH Config（如果 Key 文件名非默认）
```bash
# 在服务器上执行
cat >> ~/.ssh/config << 'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/github_deploy
EOF

chmod 600 ~/.ssh/config
```

#### 2.4 测试 SSH 连接
```bash
ssh -T git@github.com
# 应该看到: Hi username! You've successfully authenticated...
```

---

### Step 3: 配置 GitHub Secrets

#### 3.1 获取服务器信息
```bash
# 服务器 IP 地址
echo $SSH_HOST

# SSH 用户名
whoami

# SSH 端口（默认 22）
echo $SSH_PORT
```

#### 3.2 在 GitHub 配置 Secrets
1. 访问仓库页面
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 依次添加以下 Secrets：

| Secret Name | Secret Value | 示例 |
|-------------|--------------|------|
| `SSH_HOST` | 服务器 IP 地址 | `192.168.1.100` |
| `SSH_USER` | SSH 用户名 | `root` 或 `ubuntu` |
| `SSH_PASSWORD` | SSH 密码 | `your-password` |
| `SSH_PORT` | SSH 端口 | `22`（默认） |

**注意事项**:
- Secret Name 必须完全匹配（区分大小写）
- Secret Value 不要包含引号
- 配置后无法查看，只能重新设置

---

### Step 4: 创建 Dockerfile

在项目根目录创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 使用国内镜像加速（可选，国内服务器推荐）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir uv

# 复制依赖文件
COPY pyproject.toml ./

# 复制源代码
COPY src/ ./src/

# 安装依赖
RUN uv sync

# 暴露端口
EXPOSE 6100

# 启动命令
CMD ["uv", "run", "python", "-m", "src.backend.app"]
```

**关键点**:
- ✅ 先 COPY 依赖文件，再 COPY 代码（利用 Docker 缓存）
- ✅ 使用国内镜像源加速（国内服务器）
- ✅ EXPOSE 端口必须与应用端口一致

---

### Step 5: 创建 .dockerignore

在项目根目录创建 `.dockerignore`:

```
.git
.gitignore
.venv
__pycache__
*.pyc
*.pyo
*.egg-info
.pytest_cache
.coverage
htmlcov
.mypy_cache
.ruff_cache
*.md
tests/
standards/
newstandards/
environment.yml
Makefile
.github/
```

**作用**: 减小 Docker 镜像体积，加快构建速度

---

### Step 6: 创建 GitHub Actions 工作流

在项目根目录创建 `.github/workflows/ci.yml`:

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  IMAGE_NAME: your-app-name

jobs:
  ci:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 设置 Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: 安装 uv
        run: pip install uv

      - name: 安装依赖
        run: uv sync --extra dev

      - name: 代码格式检查
        run: uv run black --check .

      - name: 代码风格检查
        run: uv run ruff check .

      - name: 类型检查
        run: uv run mypy src/
        continue-on-error: true

      - name: 运行测试
        run: uv run pytest tests/ -v --cov=src/
        continue-on-error: true

  cd:
    needs: ci
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 部署到远程服务器
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          password: ${{ secrets.SSH_PASSWORD }}
          port: ${{ secrets.SSH_PORT }}
          command_timeout: 30m
          script: |
            set -e
            
            echo "=========================================="
            echo "开始 Docker 部署..."
            echo "=========================================="
            
            PROJECT_DIR="/home/${{ secrets.SSH_USER }}/your-project-name"
            IMAGE_NAME="your-app-name"
            CONTAINER_NAME="your-app-name"
            PORT=6100
            
            mkdir -p $PROJECT_DIR
            cd $PROJECT_DIR
            
            # 配置 SSH
            mkdir -p ~/.ssh
            ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
            
            # 拉取最新代码
            if [ -d ".git" ]; then
              git fetch --all
              git reset --hard origin/main
              git clean -fd
            else
              git clone git@github.com:username/repo.git .
            fi
            
            echo ">>> 当前代码版本:"
            git log -1 --oneline
            
            # 检查 Docker
            if ! command -v docker &> /dev/null; then
              echo ">>> 安装 Docker..."
              curl -fsSL https://get.docker.com | sh
              systemctl start docker
              systemctl enable docker
            fi
            
            # 构建镜像
            echo ">>> 构建 Docker 镜像..."
            docker build -t $IMAGE_NAME:latest .
            
            # 停止旧容器
            docker stop $CONTAINER_NAME 2>/dev/null || true
            docker rm $CONTAINER_NAME 2>/dev/null || true
            
            # 启动新容器
            echo ">>> 启动新容器..."
            docker run -d \
              --name $CONTAINER_NAME \
              --restart unless-stopped \
              -p $PORT:6100 \
              $IMAGE_NAME:latest
            
            sleep 3
            
            # 检查状态
            if docker ps | grep -q $CONTAINER_NAME; then
              echo "=========================================="
              echo "部署完成！"
              echo "访问地址: http://<服务器IP>:$PORT"
              echo "=========================================="
            else
              echo "错误: 容器启动失败"
              docker logs $CONTAINER_NAME
              exit 1
            fi
```

**需要修改的地方**:
- `IMAGE_NAME`: 改为你的应用名称
- `PROJECT_DIR`: 改为服务器上的项目路径
- `git clone`: 改为你的仓库地址
- `PORT`: 改为你的应用端口

---

### Step 7: 创建 .gitattributes（跨平台必需）

在项目根目录创建 `.gitattributes`:

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
```

**作用**: 避免 Windows/Linux 换行符冲突

---

## ✅ 配置验证清单

### 本地验证
- [ ] `git status` 显示工作区干净
- [ ] `uv run black --check .` 通过
- [ ] `uv run ruff check .` 通过
- [ ] `uv run pytest tests/` 通过
- [ ] `docker build -t test .` 成功

### GitHub 验证
- [ ] 推送代码后 Actions 自动触发
- [ ] CI 任务全部通过（绿色 ✓）
- [ ] CD 任务成功部署
- [ ] 访问服务器 IP:端口 可以访问

### 服务器验证
```bash
# SSH 登录服务器
ssh user@server-ip

# 检查容器状态
docker ps | grep your-app-name

# 查看容器日志
docker logs your-app-name

# 测试服务
curl http://localhost:6100
```

---

## 🔄 日常开发流程

### 1. 本地开发
```bash
# 编写代码
vim src/backend/app.py

# 运行测试
uv run pytest tests/ -v

# 代码检查
uv run black .
uv run ruff check .
```

### 2. 提交代码
```bash
git add -A
git commit -m "feat: 添加新功能"
git push
```

### 3. 自动部署
- GitHub Actions 自动触发 CI/CD
- 查看部署进度: https://github.com/username/repo/actions
- 等待部署完成（约 5-10 分钟）

### 4. 验证部署
```bash
# 访问服务
curl http://<服务器IP>:6100

# 或在浏览器打开
open http://<服务器IP>:6100
```

---

## 🎯 配置顺序总结

```
1. 创建 GitHub 仓库
   ↓
2. 配置服务器 SSH Key（私有仓库）
   ↓
3. 配置 GitHub Secrets
   ↓
4. 创建 Dockerfile
   ↓
5. 创建 .dockerignore
   ↓
6. 创建 .github/workflows/ci.yml
   ↓
7. 创建 .gitattributes
   ↓
8. 提交并推送代码
   ↓
9. 查看 GitHub Actions 执行结果
   ↓
10. 验证服务部署成功
```

---

## 📚 相关文档

- [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md) - Docker 配置模板
- [04-GITHUB-ACTIONS-TEMPLATE.md](04-GITHUB-ACTIONS-TEMPLATE.md) - CI/CD 配置模板
- [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) - 实战踩坑经验
- [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) - 常见问题排查

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理
