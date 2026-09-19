# 通用项目开发规范 v3.0（AI 驱动版）

> **目标**: 让 AI 根据一个配置文件自动生成完整项目  
> **特点**: 最少人工操作，完整 CI/CD 闭环，跨平台兼容

---

## 🎯 核心优势

### 对比旧版 standards

| 特性 | 旧 standards | 新 newstandards |
|------|-------------|----------------|
| **AI 驱动** | ❌ 无 | ✅ 完整支持 |
| **配置文件** | ❌ 分散 | ✅ 单文件配置 |
| **CI/CD 闭环** | ⚠️ 部分 | ✅ 完整 |
| **配置顺序** | ❌ 无 | ✅ 详细清单 |
| **实战经验** | ⚠️ 分散 | ✅ 系统化 |
| **跨平台** | ⚠️ 部分 | ✅ 完整 |
| **教学友好** | ⚠️ 一般 | ✅ 优秀 |
| **配置模板** | ⚠️ 部分 | ✅ 完整 |
| **问题排查** | ❌ 无 | ✅ 详细 |
| **一键生成** | ❌ 无 | ✅ 支持 |

---

## 🚀 快速开始（3 步）

**完整指南**: 请查看 [00-HOW-TO-USE.md](00-HOW-TO-USE.md)

### Step 1: 修改配置文件（1 分钟）
编辑 [PROJECT-BASE-INFO.md](PROJECT-BASE-INFO.md)，替换 `[...]` 内容

### Step 2: 发送 Prompt（30 秒）
复制 [AI-PROMPT-SIMPLE.md](AI-PROMPT-SIMPLE.md) 内容到 AI 对话框

### Step 3: 执行命令（自动）
AI 自动生成完整项目，包含代码、测试、CI/CD

### Step 4: 创建状态文件（1 分钟）
复制 [09-PROJECT-RECOVERY.md](09-PROJECT-RECOVERY.md) 中的模板，创建 `PROJECT-STATUS.md`

---

## 📁 文件结构

```
newstandards/
├── README.md                    # 本文件（总览）
├── INDEX.md                     # 文档索引
├── 00-HOW-TO-USE.md             # 完整使用指南 ⭐
│
├── 🎯 AI 驱动核心文件
│   ├── PROJECT-BASE-INFO.md     # 极简配置（唯一需要修改）⭐
│   ├── PROJECT-CONFIG.md        # 详细配置（可选）
│   ├── AI-PROMPT-SIMPLE.md      # 极简 Prompt（推荐）⭐
│   └── AI-PROMPT-TEMPLATE.md    # 完整 Prompt（高级）
│
├── 📖 核心文档
│   ├── 00-QUICK-START.md        # 快速启动指南
│   ├── 01-CICD-SETUP-GUIDE.md   # CI/CD 配置指南
│   ├── 02-PROJECT-STRUCTURE.md  # 项目结构规范
│   ├── 03-DOCKER-TEMPLATE.md    # Docker 配置模板
│   └── 04-GITHUB-ACTIONS-TEMPLATE.md # CI/CD 配置模板
│
├── 📝 开发规范与管理
│   ├── 05-LESSONS-LEARNED.md    # 实战踩坑经验
│   ├── 06-CROSS-PLATFORM-GUIDE.md # 跨平台开发指南
│   ├── 07-TROUBLESHOOTING.md    # 常见问题排查
│   ├── 08-CODE-STYLE.md         # 代码风格规范 ⭐
│   └── 09-PROJECT-RECOVERY.md   # 项目恢复指南 ⭐
│
├── 📦 配置模板
│   └── templates/
│       ├── pyproject.toml       # Python 项目配置
│       ├── Dockerfile           # Docker 镜像配置
│       ├── .gitignore           # Git 忽略文件
│       ├── .gitattributes       # Git 属性配置
│       ├── .dockerignore        # Docker 忽略文件
│       └── ci.yml               # GitHub Actions 配置
│
└── 📚 示例
    └── USAGE-EXAMPLE.md         # 完整使用示例

⭐ = 必读文档
```

---

## 🎓 使用场景

### 场景 1: 新项目快速启动
```
1. 复制 newstandards/ 到新项目
2. 修改 PROJECT-BASE-INFO.md
3. 发送 AI-PROMPT-SIMPLE.md 到 AI
4. 等待 AI 生成完整项目
5. 配置 GitHub Secrets
6. 推送代码，自动部署
```

### 场景 2: 课堂演示
```
1. 打开 00-QUICK-START.md
2. 按照 "教学演示流程" 进行
3. 30 分钟完成从需求到部署
```

### 场景 3: 问题排查
```
1. 遇到问题先查 07-TROUBLESHOOTING.md
2. 了解原理查 05-LESSONS-LEARNED.md
3. 配置参考 01-CICD-SETUP-GUIDE.md
```

---

## 🔧 配置文件说明

### PROJECT-BASE-INFO.md（极简版）
**用途**: 唯一需要修改的配置文件  
**内容**: 项目名称、描述、GitHub 信息、服务器信息、业务需求  
**修改方式**: 替换 `[...]` 中的内容

### PROJECT-CONFIG.md（详细版）
**用途**: 需要更多自定义选项时使用  
**内容**: 完整的项目配置，包括技术栈、测试、CI/CD 功能等  
**修改方式**: 勾选选项，替换 `[...]` 内容

---

## 📝 AI Prompt 说明

### AI-PROMPT-SIMPLE.md（推荐）
**用途**: 一键生成项目  
**特点**: 
- 最简单，只需粘贴配置
- 适合大多数项目
- 生成标准项目结构

### AI-PROMPT-TEMPLATE.md（高级）
**用途**: 完全自定义项目  
**特点**:
- 详细控制生成过程
- 适合特殊需求项目
- 可自定义项目结构

---

## 🔄 完整工作流程

```
┌─────────────────────────────────────────────────────────┐
│  1. 修改 PROJECT-BASE-INFO.md（1 分钟）                  │
│     - 项目名称、描述                                      │
│     - GitHub 信息                                         │
│     - 服务器信息                                          │
│     - 业务需求                                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. 发送 AI Prompt（30 秒）                              │
│     - 复制 AI-PROMPT-SIMPLE.md 内容                      │
│     - 粘贴配置文件内容                                    │
│     - 发送给 AI                                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. AI 自动生成项目（5 分钟）                             │
│     - 创建项目结构                                        │
│     - 生成配置文件                                        │
│     - 生成核心代码                                        │
│     - 生成测试代码                                        │
│     - 生成文档                                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. 执行创建命令（自动）                                  │
│     - AI 提供完整命令                                     │
│     - 复制执行即可                                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  5. 配置 GitHub Secrets（3 分钟）                        │
│     - SSH_HOST                                           │
│     - SSH_USER                                           │
│     - SSH_PASSWORD                                       │
│     - SSH_PORT                                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  6. 配置服务器 SSH Key（2 分钟，私有仓库）                │
│     - 生成 SSH Key                                        │
│     - 添加公钥到 GitHub                                   │
│     - 配置 ~/.ssh/config                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  7. 推送代码（30 秒）                                     │
│     - git remote add origin ...                          │
│     - git push -u origin main                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  8. 自动 CI/CD（自动）                                    │
│     - GitHub Actions 自动触发                             │
│     - CI: 代码检查 + 测试                                 │
│     - CD: Docker 构建部署                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  9. 验证部署（30 秒）                                     │
│     - 访问 http://<服务器IP>:<端口>                       │
│     - 验证服务运行                                        │
└─────────────────────────────────────────────────────────┘
```

**总时间**: 约 10 分钟（人工操作约 5 分钟）

---

## 📚 文档索引

### ⭐ 必读文档
- [00-HOW-TO-USE.md](00-HOW-TO-USE.md) - **完整使用指南**（从零到部署）
- [PROJECT-BASE-INFO.md](PROJECT-BASE-INFO.md) - **项目配置文件**（唯一需要修改）
- [AI-PROMPT-SIMPLE.md](AI-PROMPT-SIMPLE.md) - **AI Prompt**（一键生成项目）
- [08-CODE-STYLE.md](08-CODE-STYLE.md) - **代码风格规范**
- [09-PROJECT-RECOVERY.md](09-PROJECT-RECOVERY.md) - **项目恢复指南**（中断后快速上手）

### 快速开始
- [00-QUICK-START.md](00-QUICK-START.md) - 快速启动指南
- [USAGE-EXAMPLE.md](USAGE-EXAMPLE.md) - 完整使用示例

### 详细配置
- [PROJECT-CONFIG.md](PROJECT-CONFIG.md) - 详细配置文件
- [AI-PROMPT-TEMPLATE.md](AI-PROMPT-TEMPLATE.md) - 完整 Prompt 模板
- [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - CI/CD 配置指南

### 项目规范
- [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md) - 项目结构规范
- [03-DOCKER-TEMPLATE.md](03-DOCKER-TEMPLATE.md) - Docker 配置模板
- [04-GITHUB-ACTIONS-TEMPLATE.md](04-GITHUB-ACTIONS-TEMPLATE.md) - CI/CD 配置模板

### 经验总结
- [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) - 实战踩坑经验
- [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) - 跨平台开发指南
- [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) - 常见问题排查

### 配置模板
- [templates/](templates/) - 开箱即用的配置文件

---

## 🎯 与旧 standards 的关系

### 为什么创建 newstandards？

1. **AI 驱动**: 旧版不支持 AI 自动生成，新版完全支持
2. **配置简化**: 旧版配置分散，新版单文件配置
3. **CI/CD 闭环**: 旧版不完整，新版完整闭环
4. **实战经验**: 新版整合了完整的踩坑经验
5. **教学友好**: 新版更适合课堂演示

### 是否需要保留旧 standards？

**建议**: 保留旧 standards 作为参考，但新项目使用 newstandards

**原因**:
- 旧 standards 包含更多开发规范细节
- 新 newstandards 专注于 AI 驱动和 CI/CD
- 两者可以互补使用

---

## 🌟 核心特性

### 1. AI 驱动开发 ✅
- 单文件配置
- 一键生成项目
- 自动生成代码、测试、CI/CD

### 2. 完整 CI/CD 闭环 ✅
- CI: 代码检查 + 测试
- CD: Docker 自动部署
- 多版本 Python 测试

### 3. 跨平台兼容 ✅
- Windows / macOS / Linux
- 统一换行符（LF）
- pathlib 路径处理

### 4. 实战验证 ✅
- 基于 Match-3 游戏项目实战
- 记录 13 个常见错误
- 提供完整解决方案

### 5. 教学友好 ✅
- 30 分钟演示流程
- 清晰的文档结构
- 详细的配置步骤

---

## 📊 使用统计

| 操作 | 旧 standards | 新 newstandards |
|------|-------------|----------------|
| 配置文件数量 | 多个 | 1 个 |
| 人工操作时间 | 30+ 分钟 | 5 分钟 |
| AI 自动化程度 | 0% | 90% |
| CI/CD 配置时间 | 15+ 分钟 | 3 分钟 |
| 问题排查时间 | 未知 | 5 分钟 |

---

## 🔗 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker 文档](https://docs.docker.com/)
- [uv 文档](https://github.com/astral-sh/uv)
- [Flask 文档](https://flask.palletsprojects.com/)

---

## 📄 许可证

MIT License

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于 Match-3 游戏项目实战经验整理  
**适用场景**: AI 驱动的项目自动生成，从 Prompt 到部署的完整闭环
