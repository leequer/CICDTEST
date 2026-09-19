# 常见问题排查指南

> **目标**: 快速定位和解决 CI/CD 部署中的常见问题  
> **适用**: GitHub Actions + Docker 部署

---

## 📋 问题分类

- [CI 阶段问题](#ci-阶段问题)
- [CD 阶段问题](#cd-阶段问题)
- [Docker 问题](#docker-问题)
- [服务器问题](#服务器问题)
- [网络问题](#网络问题)

---

## CI 阶段问题

### 问题 1: 依赖安装失败

**错误信息**:
```bash
ERROR: Could not find a version that satisfies the requirement xxx
```

**可能原因**:
1. 依赖版本不兼容
2. PyPI 镜像源问题
3. Python 版本不匹配

**排查步骤**:
```bash
# 1. 检查 pyproject.toml 中的依赖版本
cat pyproject.toml

# 2. 检查 Python 版本要求
python --version

# 3. 尝试手动安装
pip install package-name

# 4. 查看详细错误
pip install package-name --verbose
```

**解决方案**:
```toml
# pyproject.toml
[project]
requires-python = ">=3.11"  # 明确 Python 版本
dependencies = [
    "flask>=3.0.0,<4.0.0",  # 指定版本范围
]
```

---

### 问题 2: 代码检查失败

**错误信息**:
```bash
black: command not found
ruff: command not found
```

**原因**: 未安装开发依赖

**解决方案**:
```yaml
# .github/workflows/ci.yml
- name: 安装依赖
  run: uv sync --extra dev  # 必须包含 --extra dev
```

---

### 问题 3: 测试失败

**错误信息**:
```bash
ModuleNotFoundError: No module named 'src'
```

**原因**: 导入路径问题

**解决方案**:
```python
# ❌ 错误
import app
from backend.app import app

# ✅ 正确
from src.backend.app import app
```

---

## CD 阶段问题

### 问题 4: SSH 连接失败

**错误信息**:
```bash
ssh: connect to host xxx.xxx.xxx.xxx port 22: Connection refused
```

**排查步骤**:
```bash
# 1. 检查服务器是否在线
ping <服务器IP>

# 2. 检查 SSH 端口
nmap -p 22 <服务器IP>

# 3. 检查防火墙
# 在服务器上执行
sudo ufw status
sudo firewall-cmd --list-all

# 4. 检查 SSH 服务
sudo systemctl status sshd
```

**解决方案**:
```bash
# 启动 SSH 服务
sudo systemctl start sshd
sudo systemctl enable sshd

# 开放 SSH 端口
sudo ufw allow 22
sudo firewall-cmd --add-service=ssh --permanent
sudo firewall-cmd --reload
```

---

### 问题 5: 认证失败

**错误信息**:
```bash
Permission denied (publickey)
```

**排查步骤**:
```bash
# 1. 检查 SSH Key 是否存在
ls -la ~/.ssh/

# 2. 检查 SSH Key 权限
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# 3. 测试 SSH 连接
ssh -T git@github.com

# 4. 查看详细日志
ssh -vvv git@github.com
```

**解决方案**:
```bash
# 如果 SSH Key 文件名非默认，配置 ~/.ssh/config
cat >> ~/.ssh/config << 'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/github_deploy
EOF

chmod 600 ~/.ssh/config
```

---

### 问题 6: Git 克隆失败

**错误信息**:
```bash
fatal: could not read Username for 'https://github.com'
```

**原因**: 私有仓库需要认证

**解决方案**: 使用 SSH 克隆
```bash
# ❌ HTTPS（私有仓库需要 Token）
git clone https://github.com/username/repo.git

# ✅ SSH（推荐）
git clone git@github.com:username/repo.git
```

---

### 问题 7: 部署超时

**错误信息**:
```bash
Run Command Timeout
```

**原因**: 
1. Docker 构建时间过长
2. 网络下载慢
3. 默认超时时间不够

**解决方案**:
```yaml
# .github/workflows/ci.yml
- uses: appleboy/ssh-action@v1.0.3
  with:
    command_timeout: 30m  # 增加超时时间
```

---

## Docker 问题

### 问题 8: 镜像构建失败

**错误信息**:
```bash
ERROR [3/6] RUN pip install --no-cache-dir uv
```

**排查步骤**:
```bash
# 1. 本地构建测试
docker build -t test:latest .

# 2. 查看详细日志
docker build --progress=plain -t test:latest .

# 3. 检查 Dockerfile 语法
cat Dockerfile
```

**常见错误**:

#### 错误 1: COPY 顺序错误
```dockerfile
# ❌ 错误
COPY pyproject.toml ./
RUN uv sync
COPY src/ ./src/

# ✅ 正确
COPY pyproject.toml ./
COPY src/ ./src/
RUN uv sync
```

#### 错误 2: 文件不存在
```dockerfile
# 检查文件是否存在
COPY requirements.txt ./  # 如果文件不存在会报错
```

---

### 问题 9: 容器启动失败

**错误信息**:
```bash
docker: Error response from daemon: driver failed programming external connectivity
```

**原因**: 端口已被占用

**排查步骤**:
```bash
# 1. 查看端口占用
netstat -tulpn | grep 6100
lsof -i :6100

# 2. 停止占用端口的进程
kill -9 <PID>

# 3. 或使用不同端口
docker run -p 6101:6100 my-app
```

---

### 问题 10: 容器运行后立即退出

**排查步骤**:
```bash
# 1. 查看容器状态
docker ps -a

# 2. 查看容器日志
docker logs <container-id>

# 3. 查看退出码
docker inspect <container-id> | grep ExitCode
```

**常见原因**:
- 应用启动失败
- 配置错误
- 依赖缺失

**解决方案**:
```bash
# 进入容器调试
docker run -it my-app:latest bash

# 手动运行启动命令
python -m src.backend.app
```

---

## 服务器问题

### 问题 11: 磁盘空间不足

**错误信息**:
```bash
No space left on device
```

**排查步骤**:
```bash
# 1. 查看磁盘使用情况
df -h

# 2. 查看目录大小
du -sh /*
du -sh /var/lib/docker/*

# 3. 查看 Docker 占用
docker system df
```

**解决方案**:
```bash
# 清理 Docker 资源
docker system prune -a --volumes

# 清理旧镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune
```

---

### 问题 12: 内存不足

**错误信息**:
```bash
Killed
```

**排查步骤**:
```bash
# 1. 查看内存使用
free -h

# 2. 查看进程内存占用
top
htop

# 3. 查看 Docker 容器资源
docker stats
```

**解决方案**:
```bash
# 限制容器内存
docker run -m 512m my-app:latest

# 或在 docker-compose.yml 中配置
services:
  app:
    mem_limit: 512m
```

---

### 问题 13: 权限问题

**错误信息**:
```bash
Permission denied
```

**排查步骤**:
```bash
# 1. 查看文件权限
ls -la

# 2. 查看当前用户
whoami

# 3. 查看 Docker 权限
groups
```

**解决方案**:
```bash
# 将用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker

# 修改文件权限
chmod +x script.sh
```

---

## 网络问题

### 问题 14: 无法访问服务

**错误信息**:
```bash
curl: (7) Failed to connect to xxx.xxx.xxx.xxx port 6100: Connection refused
```

**排查步骤**:
```bash
# 1. 检查容器是否运行
docker ps | grep my-app

# 2. 检查端口映射
docker port my-app

# 3. 检查防火墙
sudo ufw status
sudo firewall-cmd --list-all

# 4. 检查服务是否监听
netstat -tulpn | grep 6100

# 5. 在服务器内部测试
curl http://localhost:6100
```

**解决方案**:
```bash
# 开放端口
sudo ufw allow 6100
sudo firewall-cmd --add-port=6100/tcp --permanent
sudo firewall-cmd --reload

# 检查容器网络
docker inspect my-app | grep IPAddress
```

---

### 问题 15: 下载速度慢

**错误信息**:
```bash
Downloading... (100KB/s)
```

**原因**: 未使用镜像源

**解决方案**:
```dockerfile
# Dockerfile
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir uv
```

---

## 🔍 调试技巧

### 1. 查看 GitHub Actions 日志

1. 访问 `https://github.com/username/repo/actions`
2. 点击失败的工作流
3. 展开每个步骤查看详细日志
4. 搜索 "ERROR" 或 "FAILED"

### 2. SSH 登录服务器调试

```bash
# 登录服务器
ssh user@server-ip

# 查看容器状态
docker ps -a

# 查看容器日志
docker logs my-app

# 进入容器
docker exec -it my-app bash

# 查看代码版本
cd /path/to/project
git log -1 --oneline

# 手动运行命令
docker build -t test .
docker run -p 6100:6100 test
```

### 3. 本地复现问题

```bash
# 使用相同的 Docker 镜像
docker build -t my-app:latest .
docker run -p 6100:6100 my-app:latest

# 查看日志
docker logs -f my-app
```

### 4. 启用详细日志

```yaml
# .github/workflows/ci.yml
- name: 部署
  env:
    ACTIONS_STEP_DEBUG: true
  run: |
    set -x  # 显示执行的命令
    # 部署脚本
```

---

## 📚 相关文档

- [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - CI/CD 配置指南
- [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) - 实战经验总结
- [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) - 跨平台开发指南

---

## 🆘 获取帮助

### 查看日志
- GitHub Actions: `https://github.com/username/repo/actions`
- Docker: `docker logs container-name`
- 系统日志: `journalctl -xe`

### 搜索解决方案
- GitHub Issues
- Stack Overflow
- Docker Hub
- 官方文档

### 社区支持
- GitHub Discussions
- Reddit (r/docker, r/devops)
- Discord 服务器

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理
