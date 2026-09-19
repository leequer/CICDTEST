# 项目配置文件（AI 驱动开发的唯一配置）

> **重要**: 这是唯一需要手动修改的文件！  
> **用途**: AI 根据此配置自动生成完整项目  
> **修改方式**: 替换 `[...]` 中的内容

---

## 📋 项目基础信息

### 项目名称
```
[your-project-name]
```

### 项目描述
```
[简短描述项目功能，1-2 句话]
```

### 项目类型
```
选择一个:
[ ] Web 应用（Flask/FastAPI）
[ ] 数据分析项目
[ ] AI/机器学习项目
[ ] 游戏项目
[ ] API 服务
[ ] 其他: [具体说明]
```

---

## 🎯 核心需求（Prompt）

### 业务需求描述
```
[详细描述项目需求，AI 将根据此生成代码]

示例：
完整网页版消消乐游戏，具有可交互，且包含特效。
游戏交互性：构建交互式网页三消游戏，实现鼠标/触摸滑动交换、实时消除动画、连锁特效。
核心玩法机制：完成方块匹配消除 + 重力下落 + 连锁反应 + 特殊道具生成（炸弹、彩虹球、范围爆炸等）。
部署上线：将完整游戏部署为浏览器直接运行的网页应用，支持本地一键启动与 GitHub CI 自动验证。
```

### 技术栈要求
```
后端: [Flask / FastAPI / Django / 其他]
前端: [HTML+JS / React / Vue / 其他]
数据库: [SQLite / PostgreSQL / MySQL / 无]
其他: [Redis / Celery / 其他]
```

---

## 🚀 部署配置

### 本地开发
```
开发目录: [E:\CZ\gz_cz\gz_part0]
虚拟环境: [conda / venv / uv]
环境名称: [your-env-name]
启动端口: [6100]
```

### GitHub 配置
```
GitHub 用户名: [your-username]
仓库名称: [your-repo-name]
仓库类型: [public / private]
仓库地址: [https://github.com/your-username/your-repo-name]
```

### 服务器配置（CD 部署）
```
服务器 IP: [192.168.1.100]
SSH 用户名: [root / ubuntu]
SSH 端口: [22]
部署目录: [/home/user/your-project-name]
服务端口: [6100]
```

---

## 🔐 密钥配置状态

### GitHub Secrets（需手动配置）
- [ ] `SSH_HOST` - 服务器 IP
- [ ] `SSH_USER` - SSH 用户名
- [ ] `SSH_PASSWORD` - SSH 密码
- [ ] `SSH_PORT` - SSH 端口

### 服务器 SSH Key（私有仓库必需）
- [ ] 已生成 SSH Key
- [ ] 已添加公钥到 GitHub
- [ ] 已配置 `~/.ssh/config`（如需要）
- [ ] 已测试 SSH 连接

---

## 📦 项目结构偏好

### 目录结构
```
选择一个:
[ ] 标准 Web 应用结构（src/backend + src/frontend）
[ ] 数据分析结构（src/data + src/analysis + notebooks）
[ ] AI 项目结构（src/models + src/training + src/inference）
[ ] 自定义: [说明]
```

### 代码风格
```
格式化工具: [black / autopep8 / yapf]
代码检查: [ruff / flake8 / pylint]
类型检查: [mypy / pyright / 不使用]
```

---

## 🧪 测试配置

### 测试框架
```
[ ] pytest（推荐）
[ ] unittest
[ ] 不需要测试
```

### 测试覆盖率要求
```
最低覆盖率: [80%]
是否上传到 Codecov: [是 / 否]
```

---

## 🎨 可选功能

### CI/CD 功能
- [ ] 代码格式检查（black）
- [ ] 代码风格检查（ruff）
- [ ] 类型检查（mypy）
- [ ] 单元测试（pytest）
- [ ] 测试覆盖率报告
- [ ] Docker 自动部署
- [ ] 多环境部署（staging + production）

### 开发工具
- [ ] pre-commit hooks
- [ ] Makefile 快捷命令
- [ ] Docker Compose
- [ ] 数据库迁移工具
- [ ] API 文档自动生成

---

## 📝 AI 生成指令

### 使用方式
1. 修改上述配置
2. 将此文件内容复制到 AI 对话中
3. 使用以下 Prompt:

```
我需要创建一个新项目，请根据以下配置自动生成完整的项目结构、代码和 CI/CD 配置：

[粘贴 PROJECT-CONFIG.md 的内容]

请按照以下步骤执行：
1. 创建项目目录结构
2. 生成 pyproject.toml 配置
3. 生成 Dockerfile 和 .dockerignore
4. 生成 .github/workflows/ci.yml
5. 生成 .gitignore 和 .gitattributes
6. 根据业务需求生成核心代码
7. 生成测试代码
8. 生成 README.md

要求：
- 所有配置必须与 PROJECT-CONFIG.md 中的设置一致
- 代码必须符合最佳实践
- 必须包含完整的 CI/CD 配置
- 必须支持跨平台开发（Windows/macOS/Linux）
```

---

## 🔄 配置更新记录

| 日期 | 修改内容 | 修改人 |
|------|---------|--------|
| 2026-03-28 | 初始化配置 | - |

---

## 📚 相关文档

- [00-QUICK-START.md](00-QUICK-START.md) - 快速启动指南
- [01-CICD-SETUP-GUIDE.md](01-CICD-SETUP-GUIDE.md) - CI/CD 配置指南
- [AI-PROMPT-TEMPLATE.md](AI-PROMPT-TEMPLATE.md) - AI 生成项目的完整 Prompt

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**用途**: AI 驱动的项目自动生成配置
