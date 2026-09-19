# 文档索引（快速导航）

> **快速找到你需要的文档**

---

## 🚀 我想快速开始

**→ [00-QUICK-START.md](00-QUICK-START.md)**  
30 分钟从零到部署

---

## 🔧 我需要配置 CI/CD

**→ [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md)**  
完整的 CI/CD 配置步骤，包含配置顺序

**必需配置**:
1. GitHub 仓库
2. 服务器 SSH Key（私有仓库）
3. GitHub Secrets
4. Dockerfile
5. .github/workflows/ci.yml

---

## 📁 我想了解项目结构

**→ [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md)**  
标准项目目录结构和命名规范

**核心目录**:
- `src/` - 源代码
- `tests/` - 测试代码
- `.github/workflows/` - CI/CD 配置

---

## 🐳 我需要 Docker 配置

**→ [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md)**  
Dockerfile 和 docker-compose.yml 模板

**包含**:
- 基础版 Dockerfile
- 国内镜像加速版
- 多阶段构建版
- 生产环境版

---

## ⚙️ 我需要 GitHub Actions 配置

**→ [04-GITHUB-ACTIONS-TEMPLATE.md](04-GITHUB-ACTIONS-TEMPLATE.md)**  
完整的 CI/CD 工作流配置

**功能**:
- 多版本 Python 测试
- 代码检查（black, ruff, mypy）
- 自动测试
- Docker 部署

---

## 🐛 我遇到了问题

**→ [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md)**  
常见问题排查指南

**问题分类**:
- CI 阶段问题
- CD 阶段问题
- Docker 问题
- 服务器问题
- 网络问题

---

## 📚 我想学习经验

**→ [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md)**  
实战踩坑经验总结

**包含 13 个常见错误及解决方案**:
- GitHub Token 配置错误
- SSH Key 认证失败
- Docker 构建超时
- 换行符冲突
- 等等...

---

## 💻 我需要跨平台开发

**→ [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md)**  
Windows / macOS / Linux 兼容指南

**核心内容**:
- 路径处理（pathlib）
- 换行符统一（.gitattributes）
- 文件名大小写
- 环境变量管理

---

## 📦 我需要配置模板

**→ [templates/](templates/)**  
开箱即用的配置文件

**包含**:
- `pyproject.toml` - Python 项目配置
- `Dockerfile` - Docker 镜像配置
- `.gitignore` - Git 忽略文件
- `.gitattributes` - Git 属性配置
- `.dockerignore` - Docker 忽略文件
- `ci.yml` - GitHub Actions 配置

---

## 🎓 我要准备教学演示

**→ [00-QUICK-START.md](00-QUICK-START.md) 第 "教学演示流程" 部分**

**30 分钟演示流程**:
1. 需求到代码（10 分钟）
2. CI 配置（10 分钟）
3. CD 部署（10 分钟）

---

## 📋 配置顺序速查

```
1. 创建 GitHub 仓库
   ↓
2. 配置服务器 SSH Key（私有仓库）
   ├─ 生成 SSH Key
   ├─ 添加公钥到 GitHub
   └─ 配置 ~/.ssh/config
   ↓
3. 配置 GitHub Secrets
   ├─ SSH_HOST
   ├─ SSH_USER
   ├─ SSH_PASSWORD
   └─ SSH_PORT
   ↓
4. 创建项目配置文件
   ├─ Dockerfile
   ├─ .dockerignore
   ├─ .github/workflows/ci.yml
   └─ .gitattributes
   ↓
5. 提交并推送代码
   ↓
6. 查看 GitHub Actions 执行结果
   ↓
7. 验证服务部署成功
```

---

## 🔍 按场景查找

### 场景 1: 第一次使用
1. [00-QUICK-START.md](00-QUICK-START.md)
2. [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md)
3. [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md)

### 场景 2: CI/CD 配置失败
1. [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md)
2. [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md)
3. [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md)

### 场景 3: Docker 部署问题
1. [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md)
2. [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md)
3. [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md)

### 场景 4: 我要配置 Docker
1. [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md) - Docker 配置模板
2. [templates/Dockerfile](templates/Dockerfile) - Dockerfile 模板
3. [templates/.dockerignore](templates/.dockerignore) - .dockerignore 模板

### 场景 5: 跨平台开发
1. [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) - 跨平台开发指南
2. [08-CODE-STYLE.md](08-CODE-STYLE.md) - 代码风格规范
3. [templates/.gitattributes](templates/.gitattributes) - .gitattributes 模板

### 场景 6: 开发规范与管理
1. [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) - 实战经验总结
2. [08-CODE-STYLE.md](08-CODE-STYLE.md) - 代码风格规范 ⭐
3. [09-PROJECT-RECOVERY.md](09-PROJECT-RECOVERY.md) - 项目恢复指南 ⭐

### 场景 7: 新项目启动
1. 复制 [templates/](templates/) 所有文件
2. 阅读 [00-QUICK-START.md](00-QUICK-START.md)
3. 按照 [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) 配置

---

## 📊 文档优先级

| 优先级 | 文档 | 适用人群 |
|--------|------|---------|
| ⭐⭐⭐ | [00-QUICK-START.md](00-QUICK-START.md) | 所有人 |
| ⭐⭐⭐ | [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) | 所有人 |
| ⭐⭐⭐ | [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md) | 所有人 |
| ⭐⭐ | [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md) | 需要 Docker 部署 |
| ⭐⭐ | [04-GITHUB-ACTIONS-TEMPLATE.md](04-GITHUB-ACTIONS-TEMPLATE.md) | 需要自定义 CI/CD |
| ⭐⭐ | [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) | 遇到问题时 |
| ⭐⭐ | [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) | 跨平台开发 |
| ⭐ | [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) | 问题排查 |

---

## 🎯 学习路径

### 初学者路径
1. [README.md](README.md) - 了解整体
2. [00-QUICK-START.md](00-QUICK-START.md) - 快速上手
3. [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - 配置 CI/CD
4. [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) - 解决问题

### 进阶路径
1. [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md) - 深入理解结构
2. [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md) - 掌握 Docker
3. [04-GITHUB-ACTIONS-TEMPLATE.md](04-GITHUB-ACTIONS-TEMPLATE.md) - 自定义 CI/CD
4. [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) - 学习经验

### 专家路径
1. [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) - 跨平台最佳实践
2. [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) - 深入理解原理
3. [templates/](templates/) - 自定义模板

---

## 💡 快速命令

```bash
# 查看所有文档
ls -la newstandards/

# 搜索关键词
grep -r "SSH Key" newstandards/

# 查看模板文件
ls -la newstandards/templates/
```

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理
