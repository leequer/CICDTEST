# 极简 AI Prompt（一键生成项目）

> **最简单的使用方式**: 只需复制以下内容到 AI 对话框

---

## 🚀 一键 Prompt

```
# 自动生成项目指令

请根据以下配置自动生成完整的 Python 项目（包含代码、测试、CI/CD）：

---CONFIG_START---
[粘贴 PROJECT-BASE-INFO.md 的内容]
---CONFIG_END---

## 生成要求

### 项目结构
```
[项目名称]/
├── .github/workflows/ci.yml
├── src/
│   ├── backend/app.py
│   ├── core/
│   └── utils/
├── tests/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .gitattributes
├── pyproject.toml
└── README.md
```

### 必需配置
1. **pyproject.toml**: Python 3.11+, pytest, black, ruff, mypy
2. **Dockerfile**: python:3.11-slim, 清华镜像源, uv, 正确 COPY 顺序
3. **ci.yml**: CI(测试) + CD(Docker部署), 超时30分钟
4. **.gitattributes**: 统一 LF 换行符

### 代码要求
- 后端: Flask, 监听配置端口, /health 健康检查
- 业务: 根据需求描述生成
- 测试: pytest, 覆盖率 >= 80%
- 跨平台: pathlib, LF换行, 大小写严格

### 输出格式
按步骤输出：
1. 创建目录命令
2. 各配置文件内容
3. 核心代码内容
4. 测试代码内容
5. 后续配置步骤（GitHub Secrets, SSH Key）

开始生成！
```

---

## 📝 使用步骤（3 步完成）

### Step 1: 修改配置
编辑 `PROJECT-BASE-INFO.md`，替换 `[...]` 内容

### Step 2: 复制 Prompt
1. 复制上面的 Prompt
2. 将 `[粘贴 PROJECT-BASE-INFO.md 的内容]` 替换为实际配置

### Step 3: 发送给 AI
粘贴到 AI 对话框，等待生成完整项目

---

## 🎯 配置项说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| 项目名称 | 英文，用于目录和包名 | `my-game` |
| 项目描述 | 简短说明 | `消消乐游戏` |
| GitHub 用户名 | 你的 GitHub 用户名 | `zhangsan` |
| 仓库名称 | GitHub 仓库名 | `my-game` |
| 服务器 IP | 部署服务器 IP | `192.168.1.100` |
| SSH 用户名 | 服务器登录用户 | `root` |
| SSH 端口 | SSH 端口 | `22` |
| 服务端口 | 应用端口 | `6100` |
| 业务需求 | 详细需求描述 | `完整网页游戏...` |

---

## 🔄 完整流程

```
1. 修改 PROJECT-BASE-INFO.md（1 分钟）
        ↓
2. 复制 Prompt + 配置（30 秒）
        ↓
3. 发送给 AI（10 秒）
        ↓
4. AI 生成项目（自动）
        ↓
5. 执行创建命令（自动）
        ↓
6. 配置 GitHub Secrets（3 分钟）
        ↓
7. 配置服务器 SSH Key（2 分钟）
        ↓
8. 推送代码（30 秒）
        ↓
9. 自动 CI/CD（自动）
        ↓
10. 部署完成！
```

**总时间**: 约 10 分钟（其中 AI 自动生成 5 分钟）

---

## 📚 相关文档

- [PROJECT-BASE-INFO.md](PROJECT-BASE-INFO.md) - 极简配置文件
- [PROJECT-CONFIG.md](PROJECT-CONFIG.md) - 详细配置文件
- [AI-PROMPT-TEMPLATE.md](AI-PROMPT-TEMPLATE.md) - 完整 Prompt 模板

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**用途**: 一键生成项目的极简 Prompt
