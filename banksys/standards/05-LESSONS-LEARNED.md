# 实战经验总结（踩坑记录）

> **来源**: Match-3 游戏项目从开发到 CI/CD 部署的完整实战  
> **价值**: 避免重复踩坑，快速解决常见问题

---

## 📋 目录

- [CI 阶段问题](#ci-阶段问题)
- [CD 阶段问题](#cd-阶段问题)
- [Docker 部署问题](#docker-部署问题)
- [跨平台问题](#跨平台问题)
- [核心经验总结](#核心经验总结)

---

## CI 阶段问题

### ❌ 问题 1: 忘记安装 dev 依赖

**错误现象**:
```bash
black: command not found
ruff: command not found
pytest: command not found
```

**原因**: 只运行了 `uv sync`，没有安装开发依赖

**解决方案**:
```yaml
# ❌ 错误
- run: uv sync

# ✅ 正确
- run: uv sync --extra dev
```

---

### ❌ 问题 2: 测试失败导致 CI 中断

**错误现象**: 测试失败后，后续步骤不执行，CD 无法触发

**原因**: 默认情况下，任何步骤失败都会中断工作流

**解决方案**:
```yaml
- name: 运行测试
  run: uv run pytest tests/
  continue-on-error: true  # 允许失败但继续执行
```

**适用场景**: 类型检查、测试覆盖率等非阻塞性检查

---

## CD 阶段问题

### ❌ 问题 3: GitHub Token 配置错误

**错误现象**:
```bash
could not read Username for 'https://github.com'
```

**原因 1**: 私有仓库使用 HTTPS 克隆需要认证

**原因 2**: 把 Token 值当作 Secret 名称
```bash
# ❌ 错误配置
Secret Name: github_pat_11AH5WASY08A9bynzFhZQs...
Secret Value: (空)

# ✅ 正确配置
Secret Name: GH_PAT
Secret Value: github_pat_11AH5WASY08A9bynzFhZQs...
```

**终极解决方案**: 使用 SSH Key（推荐）
```bash
# 服务器上生成 SSH Key
ssh-keygen -t ed25519 -C "email@example.com" -f ~/.ssh/github_deploy

# 添加公钥到 GitHub
cat ~/.ssh/github_deploy.pub
# 复制到 https://github.com/settings/keys
```

---

### ❌ 问题 4: SSH Key 文件名非默认

**错误现象**:
```bash
Permission denied (publickey)
```

**原因**: SSH Key 文件名是 `github_deploy`，不是默认的 `id_ed25519`

**解决方案**: 配置 `~/.ssh/config`
```bash
cat >> ~/.ssh/config << 'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/github_deploy
EOF

chmod 600 ~/.ssh/config
```

---

### ❌ 问题 5: 代码未同步到最新版本

**错误现象**: 部署的代码不是最新的，或者 Dockerfile 不存在

**原因**: 服务器上有本地修改或未跟踪文件

**解决方案**:
```bash
# ❌ 错误：只用 git pull
git pull origin main

# ✅ 正确：强制同步并清理
git fetch --all
git reset --hard origin/main
git clean -fd  # 删除未跟踪文件
```

---

### ❌ 问题 6: 依赖工具未安装

**错误现象**:
```bash
pip: command not found
docker: command not found
```

**原因**: 服务器环境缺少必要工具

**解决方案**: 在部署脚本中检查并安装
```bash
# 检查 Docker
if ! command -v docker &> /dev/null; then
  echo ">>> 安装 Docker..."
  curl -fsSL https://get.docker.com | sh
  systemctl start docker
  systemctl enable docker
fi
```

---

### ❌ 问题 7: Python 版本过旧

**错误现象**:
```bash
ERROR: Package 'uv' requires a different Python: 3.6.8 not in '>=3.8'
```

**原因**: 服务器 Python 版本太旧（如 3.6.8）

**终极解决方案**: 使用 Docker
- ✅ 不依赖服务器 Python 版本
- ✅ 环境完全隔离
- ✅ 避免依赖冲突

---

## Docker 部署问题

### ❌ 问题 8: Dockerfile COPY 顺序错误

**错误现象**:
```bash
ModuleNotFoundError: No module named 'src'
```

**原因**: Dockerfile 中先运行 `uv sync`，后复制 `src/`

**错误配置**:
```dockerfile
COPY pyproject.toml ./
RUN uv sync           # ❌ 此时 src/ 还不存在
COPY src/ ./src/
```

**正确配置**:
```dockerfile
COPY pyproject.toml ./
COPY src/ ./src/      # ✅ 先复制代码
RUN uv sync           # ✅ 再安装依赖
```

---

### ❌ 问题 9: Docker 构建超时

**错误现象**:
```bash
Run Command Timeout
```

**原因**: 下载 uv (24.6 MB) 太慢，默认超时 10 分钟

**解决方案 1**: 使用国内镜像源
```dockerfile
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir uv
```

**解决方案 2**: 增加超时时间
```yaml
- uses: appleboy/ssh-action@v1.0.3
  with:
    command_timeout: 30m  # 增加到 30 分钟
```

---

### ❌ 问题 10: Dockerfile 不存在

**错误现象**:
```bash
Dockerfile: no such file or directory
```

**原因**: 服务器代码未同步到最新提交

**解决方案**: 添加 `git clean -fd`
```bash
git fetch --all
git reset --hard origin/main
git clean -fd  # 清理未跟踪文件
```

---

## 跨平台问题

### ❌ 问题 11: 换行符冲突

**错误现象**:
```bash
warning: LF will be replaced by CRLF
```

**原因**: Windows 使用 CRLF，Linux 使用 LF

**解决方案**: 配置 `.gitattributes`
```
* text=auto
*.py text eol=lf
*.sh text eol=lf
Dockerfile text eol=lf
*.yml text eol=lf
```

---

### ❌ 问题 12: 路径分隔符差异

**错误现象**: Windows 上运行正常，Linux 上报错

**原因**: 硬编码路径分隔符

**错误代码**:
```python
path = "src\\backend\\app.py"  # ❌ Windows 专用
```

**正确代码**:
```python
from pathlib import Path
path = Path("src") / "backend" / "app.py"  # ✅ 跨平台
```

---

### ❌ 问题 13: 文件名大小写

**错误现象**: macOS 上运行正常，Linux 上报错

**原因**: macOS 默认不区分大小写，Linux 区分

**错误代码**:
```python
from src.Backend.App import app  # ❌ macOS 能运行，Linux 报错
```

**正确代码**:
```python
from src.backend.app import app  # ✅ 严格匹配
```

---

## 核心经验总结

### 1. 认证方式选择

| 方式 | 适用场景 | 优缺点 |
|------|---------|--------|
| **HTTPS + Token** | 公开仓库、临时访问 | ✅ 简单<br>❌ Token 容易过期 |
| **SSH Key** | 私有仓库、长期部署 | ✅ 长期有效<br>✅ 更安全<br>❌ 配置稍复杂 |

**结论**: 私有仓库必须用 SSH Key

---

### 2. 环境隔离

| 方式 | 优缺点 |
|------|--------|
| **直接安装** | ❌ 依赖服务器环境<br>❌ Python 版本冲突<br>❌ 依赖冲突 |
| **虚拟环境** | ✅ 隔离依赖<br>❌ 仍依赖系统 Python |
| **Docker** | ✅ 完全隔离<br>✅ 环境一致<br>✅ 易于迁移 |

**结论**: Docker 是终极解决方案

---

### 3. 镜像加速

**国内服务器必须使用镜像源**:

| 类型 | 镜像源 |
|------|--------|
| **PyPI** | https://pypi.tuna.tsinghua.edu.cn/simple |
| **Docker Hub** | https://mirror.aliyuncs.com |
| **APT** | https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ |

**效果**: 下载速度从 100KB/s → 10MB/s

---

### 4. 超时配置

**Docker 构建需要足够时间**:
- 默认超时: 10 分钟
- 推荐超时: 30 分钟
- 配置位置: `command_timeout: 30m`

---

### 5. 代码同步

**强制同步三步骤**:
```bash
git fetch --all           # 获取所有更新
git reset --hard origin/main  # 强制重置到远程
git clean -fd             # 清理未跟踪文件
```

**避免问题**:
- ✅ 本地修改不干扰部署
- ✅ 未跟踪文件不影响构建
- ✅ 确保代码版本一致

---

### 6. 跨平台兼容

**三大原则**:
1. **使用 pathlib 处理路径**
   ```python
   from pathlib import Path
   path = Path("src") / "backend" / "app.py"
   ```

2. **配置 .gitattributes 统一换行符**
   ```
   * text=auto
   *.py text eol=lf
   ```

3. **严格匹配文件名大小写**
   ```python
   from src.backend.app import app  # 不是 Backend 或 App
   ```

---

## 🎯 最佳实践清单

### 开发阶段
- [ ] 使用 `pyproject.toml` 管理依赖
- [ ] 配置 `.gitignore` 排除虚拟环境
- [ ] 配置 `.gitattributes` 统一换行符
- [ ] 使用 `pathlib` 处理路径
- [ ] 严格匹配文件名大小写

### CI 配置
- [ ] 多版本 Python 测试矩阵
- [ ] 使用 `uv sync --extra dev` 安装依赖
- [ ] 非阻塞检查使用 `continue-on-error: true`
- [ ] 缓存依赖加速构建

### CD 配置
- [ ] 私有仓库使用 SSH Key
- [ ] 配置 GitHub Secrets
- [ ] 服务器配置 `~/.ssh/config`（如需要）
- [ ] 使用 `git reset --hard` + `git clean -fd`
- [ ] 增加 `command_timeout: 30m`

### Docker 配置
- [ ] Dockerfile 层级优化（依赖 → 代码）
- [ ] 使用国内镜像源（国内服务器）
- [ ] 配置 `.dockerignore` 排除无关文件
- [ ] 容器设置 `--restart unless-stopped`
- [ ] 暴露正确端口

---

## 📚 相关文档

- [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - CI/CD 配置指南
- [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) - 跨平台开发指南
- [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) - 常见问题排查

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**来源**: Match-3 游戏项目实战经验
