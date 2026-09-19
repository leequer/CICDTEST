# 跨平台开发指南

> **目标**: 确保代码在 Windows / macOS / Linux 上都能正常运行  
> **重点**: 路径、换行符、文件名大小写

---

## 📋 跨平台差异对比

| 特性 | Windows | macOS | Linux |
|------|---------|-------|-------|
| **路径分隔符** | `\` | `/` | `/` |
| **换行符** | CRLF (`\r\n`) | LF (`\n`) | LF (`\n`) |
| **文件名大小写** | 不区分 | 默认不区分 | 区分 |
| **默认 Shell** | PowerShell/CMD | Bash/Zsh | Bash |
| **Python 命令** | `python` | `python3` | `python3` |

---

## 🔧 解决方案

### 1. 路径处理

#### ❌ 错误方式

```python
# 硬编码路径分隔符
path = "src\\backend\\app.py"  # Windows 专用
path = "src/backend/app.py"    # Unix 专用

# 字符串拼接
path = "src" + os.sep + "backend" + os.sep + "app.py"  # 繁琐
```

#### ✅ 正确方式

```python
from pathlib import Path

# 使用 pathlib（推荐）
path = Path("src") / "backend" / "app.py"
print(path)  # Windows: src\backend\app.py
             # Unix: src/backend/app.py

# 获取绝对路径
abs_path = path.resolve()

# 检查文件是否存在
if path.exists():
    print("文件存在")

# 读取文件
content = path.read_text()

# 写入文件
path.write_text("Hello World")
```

#### 常用 pathlib 操作

```python
from pathlib import Path

# 当前工作目录
cwd = Path.cwd()

# 用户主目录
home = Path.home()

# 文件名和扩展名
path = Path("src/backend/app.py")
print(path.name)       # app.py
print(path.stem)       # app
print(path.suffix)     # .py
print(path.parent)     # src/backend

# 遍历目录
for file in Path("src").rglob("*.py"):
    print(file)

# 创建目录
Path("data/output").mkdir(parents=True, exist_ok=True)
```

---

### 2. 换行符处理

#### 问题说明

- Windows: `\r\n` (CRLF)
- Unix (macOS/Linux): `\n` (LF)
- 混用会导致 Git 警告、脚本执行失败

#### ✅ 解决方案：配置 .gitattributes

在项目根目录创建 `.gitattributes`:

```
# 自动检测文本文件并转换换行符
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

# 二进制文件不转换
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.woff binary
*.woff2 binary
*.ttf binary
*.eot binary
```

#### Git 配置

```bash
# 全局配置（推荐）
git config --global core.autocrlf input  # macOS/Linux
git config --global core.autocrlf true   # Windows

# 项目配置
git config core.autocrlf input
```

#### 转换现有文件

```bash
# 重新规范化所有文件
git add --renormalize .
git commit -m "chore: 规范化换行符"
```

---

### 3. 文件名大小写

#### 问题说明

- Windows: 不区分大小写 (`App.py` == `app.py`)
- macOS: 默认不区分大小写（可配置）
- Linux: 严格区分大小写 (`App.py` ≠ `app.py`)

#### ❌ 常见错误

```python
# macOS/Windows 上能运行，Linux 上报错
from src.Backend.App import app  # ❌
from src.backend.app import App  # ❌
```

#### ✅ 正确方式

```python
# 严格匹配文件名和模块名
from src.backend.app import app  # ✅
```

#### 最佳实践

1. **统一命名规范**
   - 文件名: `snake_case.py`
   - 类名: `PascalCase`
   - 函数名: `snake_case`
   - 常量: `UPPER_CASE`

2. **避免大小写混用**
   ```
   ✅ src/backend/app.py
   ✅ src/utils/helpers.py
   ❌ src/Backend/App.py
   ❌ src/Utils/Helpers.py
   ```

3. **Git 配置区分大小写**
   ```bash
   git config core.ignorecase false
   ```

---

### 4. Shell 脚本

#### 问题说明

- Windows: PowerShell / CMD
- Unix: Bash / Zsh

#### ✅ 解决方案：使用 Python 脚本

```python
# scripts/deploy.py
import subprocess
import sys
from pathlib import Path

def main():
    # 跨平台命令
    subprocess.run([sys.executable, "-m", "pytest", "tests/"])
    
if __name__ == "__main__":
    main()
```

#### 或使用 Makefile（需要安装 make）

```makefile
# Makefile
.PHONY: test install deploy

test:
	uv run pytest tests/ -v

install:
	uv sync --extra dev

deploy:
	uv run python -m src.backend.app
```

---

### 5. 环境变量

#### ❌ 错误方式

```python
# 硬编码路径
DATABASE_URL = "C:\\Users\\user\\data\\db.sqlite"  # Windows 专用
```

#### ✅ 正确方式

```python
import os
from pathlib import Path

# 使用环境变量
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/db.sqlite")

# 使用相对路径
DATA_DIR = Path(__file__).parent.parent / "data"
DATABASE_PATH = DATA_DIR / "db.sqlite"
```

#### .env 文件

```bash
# .env
DATABASE_URL=sqlite:///data/db.sqlite
API_KEY=your-api-key
DEBUG=True
```

```python
# 加载 .env
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
DEBUG = os.getenv("DEBUG", "False") == "True"
```

---

### 6. Python 命令

#### 问题说明

- Windows: `python`
- Unix: `python3`

#### ✅ 解决方案

```bash
# 使用 python -m（推荐）
python -m pytest tests/
python -m src.backend.app

# 使用 uv run（推荐）
uv run pytest tests/
uv run python -m src.backend.app

# 使用 sys.executable
import sys
import subprocess
subprocess.run([sys.executable, "-m", "pytest", "tests/"])
```

---

## 🎯 跨平台开发清单

### 代码层面
- [ ] 使用 `pathlib.Path` 处理路径
- [ ] 使用 `os.getenv()` 读取环境变量
- [ ] 严格匹配文件名大小写
- [ ] 使用 `python -m` 运行模块
- [ ] 避免硬编码路径和分隔符

### 配置层面
- [ ] 创建 `.gitattributes` 统一换行符
- [ ] 配置 `git config core.autocrlf`
- [ ] 使用 `.env` 文件管理环境变量
- [ ] 提供 `.env.example` 模板

### 测试层面
- [ ] 在多个平台上测试
- [ ] 使用 Docker 模拟 Linux 环境
- [ ] CI/CD 在 Linux 上运行测试

---

## 🐳 使用 Docker 确保一致性

### 本地开发

```bash
# 构建镜像
docker build -t my-app:latest .

# 运行容器
docker run -p 6100:6100 my-app:latest

# 进入容器调试
docker run -it my-app:latest bash
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "6100:6100"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/db.sqlite
```

---

## 🔍 常见问题排查

### 问题 1: 脚本在 Linux 上无法执行

**错误**:
```bash
bash: ./script.sh: /bin/bash^M: bad interpreter
```

**原因**: 脚本使用 CRLF 换行符

**解决**:
```bash
# 转换为 LF
dos2unix script.sh

# 或使用 sed
sed -i 's/\r$//' script.sh
```

### 问题 2: 导入模块失败

**错误**:
```python
ModuleNotFoundError: No module named 'src.Backend'
```

**原因**: 文件名大小写不匹配

**解决**: 检查实际文件名，严格匹配
```bash
ls -la src/
# 如果是 backend/ 而不是 Backend/
from src.backend.app import app
```

### 问题 3: 路径不存在

**错误**:
```python
FileNotFoundError: [Errno 2] No such file or directory: 'data\\output'
```

**原因**: 硬编码 Windows 路径分隔符

**解决**: 使用 pathlib
```python
from pathlib import Path
output_dir = Path("data") / "output"
output_dir.mkdir(parents=True, exist_ok=True)
```

---

## 📚 相关文档

- [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md) - 项目结构规范
- [05-LESSONS-LEARNED.md](05-LESSONS-LEARNED.md) - 实战经验总结
- [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) - 常见问题排查

---

## 🔗 参考资源

- [pathlib 文档](https://docs.python.org/3/library/pathlib.html)
- [Git 换行符处理](https://docs.github.com/en/get-started/getting-started-with-git/configuring-git-to-handle-line-endings)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理
