# Docker 配置模板

> **目标**: 提供开箱即用的 Docker 配置  
> **适用**: Python Web 应用、API 服务、数据处理等

---

## 📋 文件清单

- `Dockerfile` - Docker 镜像构建配置
- `.dockerignore` - Docker 构建忽略文件
- `docker-compose.yml` - 多容器编排（可选）

---

## 🐳 Dockerfile 模板

### 基础版（Flask/FastAPI）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装 uv
RUN pip install --no-cache-dir uv

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

### 国内镜像加速版

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 使用清华大学 PyPI 镜像
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

### 多阶段构建版（优化镜像大小）

```dockerfile
# 构建阶段
FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY src/ ./src/

RUN uv sync

# 运行阶段
FROM python:3.11-slim

WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 6100

CMD ["python", "-m", "src.backend.app"]
```

### 生产环境版（使用 Gunicorn）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY src/ ./src/

RUN uv sync && \
    uv add gunicorn

EXPOSE 6100

# 使用 Gunicorn 启动（4 个 worker）
CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:6100", "src.backend.app:app"]
```

---

## 🚫 .dockerignore 模板

```
# Git
.git
.gitignore
.gitattributes

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
tests/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff
.ruff_cache/

# Environment
.env
.env.local

# Documentation
*.md
docs/
newstandards/
standards/

# CI/CD
.github/

# Data
data/
notebooks/

# Build tools
Makefile
environment.yml
pyproject.toml.bak

# OS
.DS_Store
Thumbs.db
```

---

## 🔧 docker-compose.yml 模板

### 单服务版

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: my-app
    ports:
      - "6100:6100"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### 多服务版（应用 + 数据库）

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: my-app
    ports:
      - "6100:6100"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    container_name: my-db
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### 完整版（应用 + 数据库 + Redis）

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: my-app
    ports:
      - "6100:6100"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    container_name: my-db
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: my-redis
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## 🚀 常用 Docker 命令

### 构建镜像

```bash
# 基础构建
docker build -t my-app:latest .

# 指定 Dockerfile
docker build -f Dockerfile.prod -t my-app:prod .

# 不使用缓存
docker build --no-cache -t my-app:latest .

# 查看构建历史
docker history my-app:latest
```

### 运行容器

```bash
# 基础运行
docker run -d -p 6100:6100 --name my-app my-app:latest

# 挂载卷
docker run -d -p 6100:6100 -v $(pwd)/data:/app/data --name my-app my-app:latest

# 设置环境变量
docker run -d -p 6100:6100 -e FLASK_ENV=production --name my-app my-app:latest

# 自动重启
docker run -d -p 6100:6100 --restart unless-stopped --name my-app my-app:latest
```

### 管理容器

```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看容器日志
docker logs my-app

# 实时查看日志
docker logs -f my-app

# 进入容器
docker exec -it my-app bash

# 停止容器
docker stop my-app

# 启动容器
docker start my-app

# 重启容器
docker restart my-app

# 删除容器
docker rm my-app

# 强制删除运行中的容器
docker rm -f my-app
```

### 管理镜像

```bash
# 查看镜像列表
docker images

# 删除镜像
docker rmi my-app:latest

# 清理未使用的镜像
docker image prune

# 清理所有未使用的资源
docker system prune -a
```

### 使用 docker-compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止所有服务
docker-compose down

# 停止并删除卷
docker-compose down -v

# 重新构建并启动
docker-compose up -d --build
```

---

## 🎯 最佳实践

### 1. 镜像优化

#### ✅ 使用多阶段构建
```dockerfile
FROM python:3.11-slim AS builder
# 构建依赖

FROM python:3.11-slim
# 只复制必要文件
```

#### ✅ 合并 RUN 命令
```dockerfile
# ❌ 错误：多层
RUN pip install uv
RUN uv sync

# ✅ 正确：单层
RUN pip install uv && uv sync
```

#### ✅ 利用缓存
```dockerfile
# 先复制依赖文件
COPY pyproject.toml ./
RUN uv sync

# 后复制代码（代码变更不影响依赖缓存）
COPY src/ ./src/
```

### 2. 安全性

#### ✅ 不要在镜像中存储敏感信息
```dockerfile
# ❌ 错误
ENV DATABASE_PASSWORD=secret123

# ✅ 正确：运行时传入
docker run -e DATABASE_PASSWORD=secret123 my-app
```

#### ✅ 使用非 root 用户
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

#### ✅ 扫描漏洞
```bash
docker scan my-app:latest
```

### 3. 日志管理

#### ✅ 输出到 stdout/stderr
```python
import logging
logging.basicConfig(level=logging.INFO)
```

#### ✅ 限制日志大小
```bash
docker run --log-opt max-size=10m --log-opt max-file=3 my-app
```

### 4. 健康检查

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:6100/health || exit 1
```

---

## 🔍 调试技巧

### 1. 查看构建过程
```bash
docker build --progress=plain -t my-app:latest .
```

### 2. 进入失败的构建阶段
```bash
# 找到失败的中间镜像 ID
docker images -a

# 运行该镜像
docker run -it <image-id> bash
```

### 3. 查看容器资源使用
```bash
docker stats my-app
```

### 4. 导出容器文件系统
```bash
docker export my-app > my-app.tar
```

---

## 📚 相关文档

- [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - CI/CD 配置指南
- [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md) - 项目结构规范
- [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) - 常见问题排查

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理
