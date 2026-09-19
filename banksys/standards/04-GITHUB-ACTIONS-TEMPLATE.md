# GitHub Actions 配置模板

> **目标**: 提供完整的 CI/CD 工作流配置  
> **功能**: 代码检查、测试、Docker 部署

---

## 📋 完整配置模板

### 基础版（CI + CD）

文件位置: `.github/workflows/ci.yml`

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
            
            mkdir -p ~/.ssh
            ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
            
            if [ -d ".git" ]; then
              git fetch --all
              git reset --hard origin/main
              git clean -fd
            else
              git clone git@github.com:username/repo.git .
            fi
            
            echo ">>> 当前代码版本:"
            git log -1 --oneline
            
            if ! command -v docker &> /dev/null; then
              echo ">>> 安装 Docker..."
              curl -fsSL https://get.docker.com | sh
              systemctl start docker
              systemctl enable docker
            fi
            
            echo ">>> 构建 Docker 镜像..."
            docker build -t $IMAGE_NAME:latest .
            
            docker stop $CONTAINER_NAME 2>/dev/null || true
            docker rm $CONTAINER_NAME 2>/dev/null || true
            
            echo ">>> 启动新容器..."
            docker run -d \
              --name $CONTAINER_NAME \
              --restart unless-stopped \
              -p $PORT:6100 \
              $IMAGE_NAME:latest
            
            sleep 3
            
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

---

## 🎯 配置说明

### 触发条件

```yaml
on:
  push:
    branches: [main]          # main 分支推送时触发
  pull_request:
    branches: [main]          # PR 到 main 时触发
```

### 多版本测试矩阵

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']  # 测试多个 Python 版本
```

### 环境变量

```yaml
env:
  IMAGE_NAME: your-app-name   # Docker 镜像名称
```

### 任务依赖

```yaml
cd:
  needs: ci                   # CD 任务依赖 CI 任务完成
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

---

## 🔧 高级配置

### 1. 添加测试覆盖率报告

```yaml
- name: 运行测试
  run: uv run pytest tests/ -v --cov=src/ --cov-report=xml

- name: 上传覆盖率报告
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage.xml
    token: ${{ secrets.CODECOV_TOKEN }}
```

### 2. 缓存依赖加速构建

```yaml
- name: 缓存 uv 依赖
  uses: actions/cache@v3
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-uv-
```

### 3. 构建 Docker 镜像并推送到 Registry

```yaml
- name: 登录 Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}

- name: 构建并推送镜像
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: username/app:latest
```

### 4. 多环境部署

```yaml
deploy-staging:
  needs: ci
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/develop'
  steps:
    - name: 部署到测试环境
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ secrets.STAGING_HOST }}
        # ...

deploy-production:
  needs: ci
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - name: 部署到生产环境
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ secrets.PROD_HOST }}
        # ...
```

### 5. Slack 通知

```yaml
- name: 发送 Slack 通知
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'CI/CD 流程完成'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 6. 定时任务

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # 每天 UTC 0:00 运行
```

---

## 📝 必需的 GitHub Secrets

在仓库 Settings → Secrets and variables → Actions 中配置：

| Secret Name | 说明 | 示例 |
|-------------|------|------|
| `SSH_HOST` | 服务器 IP 地址 | `192.168.1.100` |
| `SSH_USER` | SSH 用户名 | `root` 或 `ubuntu` |
| `SSH_PASSWORD` | SSH 密码 | `your-password` |
| `SSH_PORT` | SSH 端口 | `22` |

可选 Secrets:

| Secret Name | 说明 | 用途 |
|-------------|------|------|
| `CODECOV_TOKEN` | Codecov 令牌 | 上传测试覆盖率 |
| `DOCKER_USERNAME` | Docker Hub 用户名 | 推送镜像 |
| `DOCKER_PASSWORD` | Docker Hub 密码 | 推送镜像 |
| `SLACK_WEBHOOK` | Slack Webhook URL | 发送通知 |

---

## 🎨 工作流变体

### 仅 CI（不部署）

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install uv
      - run: uv sync --extra dev
      - run: uv run pytest tests/ -v
```

### 仅 CD（手动触发）

```yaml
name: Deploy

on:
  workflow_dispatch:  # 手动触发

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: 部署到服务器
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SSH_HOST }}
          # ...
```

### 多任务并行

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install uv
      - run: uv sync --extra dev
      - run: uv run black --check .
      - run: uv run ruff check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install uv
      - run: uv sync --extra dev
      - run: uv run pytest tests/ -v

  deploy:
    needs: [lint, test]  # 等待两个任务都完成
    runs-on: ubuntu-latest
    steps:
      # 部署步骤
```

---

## 🔍 调试技巧

### 1. 查看工作流日志
- 访问 `https://github.com/username/repo/actions`
- 点击具体的工作流运行
- 展开每个步骤查看详细日志

### 2. 启用调试日志
在仓库 Settings → Secrets 中添加：
- `ACTIONS_RUNNER_DEBUG`: `true`
- `ACTIONS_STEP_DEBUG`: `true`

### 3. 使用 tmate 调试
```yaml
- name: Setup tmate session
  uses: mxschmitt/action-tmate@v3
  if: failure()
```

### 4. 本地测试工作流
使用 [act](https://github.com/nektos/act):
```bash
# 安装 act
brew install act  # macOS
choco install act  # Windows

# 运行工作流
act push
```

---

## ⚡ 性能优化

### 1. 使用缓存
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/pyproject.toml') }}
```

### 2. 并行执行
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
  max-parallel: 2  # 最多并行 2 个任务
```

### 3. 跳过不必要的步骤
```yaml
- name: 运行测试
  if: github.event_name == 'push'  # 只在 push 时运行
  run: uv run pytest tests/
```

---

## 📚 相关文档

- [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - CI/CD 配置指南
- [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md) - Docker 配置模板
- [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) - 常见问题排查

---

## 🔗 官方资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Workflow 语法](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理
