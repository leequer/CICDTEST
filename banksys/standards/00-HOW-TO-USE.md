# 完整使用指南（从零到部署）

> **目标**: 最易用、最可靠的 AI 驱动项目开发流程  
> **特点**: 自洽闭环，支持中断恢复

---

## 🎯 使用场景

### 场景 1: 创建新项目
从零开始，AI 自动生成完整项目

### 场景 2: 继续开发
项目中断后，快速恢复上下文

### 场景 3: 接手项目
接手他人项目，快速了解状态

---

## 📋 前置准备

### 必需工具
- [ ] Git
- [ ] Python 3.11+
- [ ] uv（`pip install uv`）
- [ ] GitHub 账号
- [ ] 服务器（如需部署）

### 必需配置
- [ ] GitHub Token（私有仓库）
- [ ] 服务器 SSH 访问
- [ ] GitHub Secrets 配置

---

## 🚀 场景 1: 创建新项目（10 分钟）

### Step 1: 复制 newstandards（30 秒）

```bash
# 创建项目目录
mkdir my-new-project
cd my-new-project

# 复制 newstandards
cp -r /path/to/newstandards ./newstandards
```

### Step 2: 修改配置文件（1 分钟）

编辑 `newstandards/PROJECT-BASE-INFO.md`:

```markdown
# 项目配置（唯一需要修改的文件）

## 基本信息
项目名称: my-new-project
项目描述: 我的新项目
GitHub 用户名: your-username
仓库名称: my-new-project

## 部署配置
服务器 IP: 192.168.1.100
SSH 用户名: root
SSH 端口: 22
服务端口: 6100

## 业务需求
[详细描述你的项目需求]
```

### Step 3: 发送 AI Prompt（30 秒）

复制 `newstandards/AI-PROMPT-SIMPLE.md` 内容，替换配置后发送给 AI

### Step 4: AI 生成项目（5 分钟）

AI 自动生成：
- 项目结构
- 配置文件
- 核心代码
- 测试代码
- 文档

### Step 5: 执行创建命令（自动）

按照 AI 提供的命令执行：

```bash
# 创建目录结构
mkdir -p src/backend src/core src/utils tests
mkdir -p .github/workflows

# 创建文件（AI 会提供完整内容）
# ...

# 初始化 Git
git init
git add -A
git commit -m "feat: 初始化项目"
```

### Step 6: 创建项目状态文件（1 分钟）

复制 `newstandards/09-PROJECT-RECOVERY.md` 中的模板，创建 `PROJECT-STATUS.md`:

```markdown
# 项目状态看板

**最后更新**: 2026-03-28 10:00  
**更新人**: your-name

---

## 📊 项目基本信息

- **项目名称**: my-new-project
- **项目描述**: 我的新项目
- **当前版本**: v0.1.0
- **GitHub 仓库**: https://github.com/your-username/my-new-project
- **部署地址**: 待部署

---

## ✅ 已完成模块

- [x] 项目结构创建
- [x] 基础配置文件
- [x] CI/CD 配置

---

## 🚧 进行中模块

- [ ] 核心功能开发（0%）

---

## 📝 待启动模块

- [ ] 功能 1
- [ ] 功能 2

---

## 🎯 下一步计划

1. 开发核心功能
2. 编写测试
3. 部署到服务器

---

**版本**: v1.0
```

### Step 7: 配置 GitHub（3 分钟）

```bash
# 创建 GitHub 仓库
# 访问 https://github.com/new

# 配置 GitHub Secrets
# 访问 https://github.com/your-username/my-new-project/settings/secrets/actions
# 添加: SSH_HOST, SSH_USER, SSH_PASSWORD, SSH_PORT

# 配置服务器 SSH Key（私有仓库）
ssh root@192.168.1.100
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub
# 复制公钥到 https://github.com/settings/keys
```

### Step 8: 推送代码（30 秒）

```bash
git remote add origin git@github.com:your-username/my-new-project.git
git branch -M main
git push -u origin main
```

### Step 9: 验证部署（30 秒）

```bash
# 查看 GitHub Actions
# 访问 https://github.com/your-username/my-new-project/actions

# 验证服务
curl http://192.168.1.100:6100/health
```

---

## 🔄 场景 2: 继续开发（1 分钟）

### Step 1: 查看项目状态（30 秒）

```bash
cd /path/to/project
cat PROJECT-STATUS.md
git log -5 --oneline
```

### Step 2: 发送恢复 Prompt（30 秒）

```
# 项目恢复指令

我需要继续开发这个项目，请帮我快速恢复上下文。

## 项目状态
[粘贴 PROJECT-STATUS.md 的内容]

## 项目配置
[粘贴 newstandards/PROJECT-BASE-INFO.md 的内容]

## 请执行以下操作
1. 阅读项目状态，确认当前进度
2. 查看"进行中模块"，了解当前任务
3. 查看"已知问题"，了解需要解决的问题
4. 告诉我当前正在做什么，下一步应该做什么

开始恢复！
```

### Step 3: 继续开发（自动）

AI 自动分析并告诉你：
- 当前进度
- 当前任务
- 下一步操作
- 需要注意的问题

---

## 👥 场景 3: 接手项目（2 分钟）

### Step 1: 克隆项目（30 秒）

```bash
git clone git@github.com:username/project.git
cd project
```

### Step 2: 查看项目文档（1 分钟）

```bash
# 查看项目状态
cat PROJECT-STATUS.md

# 查看项目配置
cat newstandards/PROJECT-BASE-INFO.md

# 查看 README
cat README.md
```

### Step 3: 发送接手 Prompt（30 秒）

```
# 项目接手指令

我需要接手这个项目，请帮我快速了解项目状态。

## 项目状态
[粘贴 PROJECT-STATUS.md]

## 项目配置
[粘贴 PROJECT-BASE-INFO.md]

## 请告诉我
1. 项目的核心功能是什么
2. 当前开发到什么阶段
3. 有哪些已知问题
4. 代码结构是怎样的
5. 如何本地运行和测试
6. 如何部署

开始介绍！
```

---

## 📝 日常开发流程

### 每天开始开发

```bash
# 1. 查看项目状态
cat PROJECT-STATUS.md

# 2. 拉取最新代码
git pull

# 3. 发送恢复 Prompt 给 AI
# [使用场景 2 的 Prompt]

# 4. 开始开发
```

### 开发过程中

```bash
# 1. 完成一个功能
git add .
git commit -m "feat: 完成 XXX 功能"

# 2. 更新项目状态
# 编辑 PROJECT-STATUS.md，标记完成的模块

# 3. 推送代码
git push

# 4. 查看 CI/CD 结果
# 访问 GitHub Actions
```

### 每天结束开发

```bash
# 1. 更新项目状态
vim PROJECT-STATUS.md
# 更新"最后更新"时间
# 更新"进行中模块"进度
# 记录"已知问题"

# 2. 提交状态文件
git add PROJECT-STATUS.md
git commit -m "docs: 更新项目状态"
git push
```

---

## 🔧 常用命令

### 本地开发

```bash
# 安装依赖
uv sync

# 运行服务
uv run python -m src.backend.app

# 运行测试
uv run pytest tests/

# 代码格式化
uv run black .

# 代码检查
uv run ruff check .
```

### Git 操作

```bash
# 查看状态
git status

# 查看最近提交
git log -5 --oneline

# 创建分支
git checkout -b feature/new-feature

# 合并分支
git checkout main
git merge feature/new-feature
```

### Docker 操作

```bash
# 构建镜像
docker build -t my-project .

# 运行容器
docker run -d -p 6100:6100 --name my-project my-project

# 查看日志
docker logs my-project

# 停止容器
docker stop my-project
```

---

## 🎯 自洽闭环检查清单

### 项目创建阶段
- [ ] 已复制 newstandards
- [ ] 已修改 PROJECT-BASE-INFO.md
- [ ] 已发送 AI Prompt
- [ ] AI 已生成完整项目
- [ ] 已创建 PROJECT-STATUS.md
- [ ] 已配置 GitHub Secrets
- [ ] 已配置服务器 SSH Key
- [ ] 已推送代码
- [ ] CI/CD 运行成功
- [ ] 服务部署成功

### 日常开发阶段
- [ ] 每天开始前查看 PROJECT-STATUS.md
- [ ] 每天结束后更新 PROJECT-STATUS.md
- [ ] 完成功能后更新状态
- [ ] 发现问题后记录到状态文件
- [ ] 做出决策后记录到状态文件

### 项目交接阶段
- [ ] PROJECT-STATUS.md 是最新的
- [ ] README.md 是完整的
- [ ] 所有配置文件都有注释
- [ ] 已知问题都已记录
- [ ] 关键决策都已记录

---

## 📊 效率对比

| 操作 | 传统方式 | 使用 newstandards |
|------|---------|------------------|
| 创建新项目 | 2+ 小时 | 10 分钟 |
| 项目恢复 | 10+ 分钟 | 1 分钟 |
| 项目交接 | 1+ 小时 | 2 分钟 |
| 问题排查 | 30+ 分钟 | 5 分钟 |
| CI/CD 配置 | 1+ 小时 | 3 分钟 |

---

## 🚨 常见问题

### Q1: AI 生成的代码有问题怎么办？
**A**: 查看 [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md)

### Q2: CI/CD 失败怎么办？
**A**: 查看 [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md)

### Q3: 如何添加新功能？
**A**: 
1. 更新 PROJECT-STATUS.md，添加到"待启动模块"
2. 发送 Prompt 给 AI，描述新功能
3. AI 生成代码
4. 测试、提交、部署

### Q4: 如何处理多人协作？
**A**:
1. 每人在自己的分支开发
2. 每天更新 PROJECT-STATUS.md
3. 合并前同步状态文件
4. 使用 Pull Request 进行代码审查

---

## 📚 相关文档

### 快速开始
- [PROJECT-BASE-INFO.md](PROJECT-BASE-INFO.md) - 项目配置
- [AI-PROMPT-SIMPLE.md](AI-PROMPT-SIMPLE.md) - AI Prompt
- [USAGE-EXAMPLE.md](USAGE-EXAMPLE.md) - 使用示例

### 开发规范
- [08-CODE-STYLE.md](08-CODE-STYLE.md) - 代码风格
- [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md) - 项目结构
- [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) - 跨平台

### 项目管理
- [09-PROJECT-RECOVERY.md](09-PROJECT-RECOVERY.md) - 项目恢复
- [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) - 经验总结
- [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) - 问题排查

---

## 🎓 最佳实践

### 1. 始终维护 PROJECT-STATUS.md
- 每天更新
- 记录所有重要决策
- 记录所有已知问题

### 2. 使用 AI 辅助开发
- 清晰描述需求
- 提供完整上下文
- 验证生成的代码

### 3. 保持代码质量
- 运行代码检查
- 编写测试
- 代码审查

### 4. 及时提交代码
- 小步提交
- 清晰的提交信息
- 及时推送

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理  
**用途**: 完整的使用指南，从零到部署
