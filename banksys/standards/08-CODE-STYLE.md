# 代码风格规范

> **目标**: 确保代码清晰、专业、可维护  
> **适用**: AI 生成的所有代码

---

## 📋 通用原则

### 1. 代码质量要求
- ✅ 清晰、专业、可维护、可搜索
- ✅ 使用简体中文注释和文档
- ✅ 禁止使用 emoji（😊🚀等）
- ✅ 遵循 PEP 8 规范

### 2. 导入规范（强制）
```python
# ✅ 正确：使用绝对导入
from src.backend.app import create_app
from src.core.models import User
from src.utils.logger import setup_logger

# ❌ 错误：相对导入
from .app import create_app
from ..core.models import User
```

**原因**: 
- 绝对导入在任何环境下都能正确解析
- 避免 `ModuleNotFoundError`
- 跨平台兼容性更好

### 3. 路径处理（强制）
```python
# ✅ 正确：使用 pathlib
from pathlib import Path

project_root = Path(__file__).parent.parent
config_file = project_root / "config" / "settings.json"

# ❌ 错误：使用字符串拼接
import os
config_file = os.path.join(project_root, "config", "settings.json")
```

**原因**:
- pathlib 自动处理不同操作系统的路径分隔符
- 更安全、更易读

---

## 🎨 代码格式化

### 工具配置

**pyproject.toml**:
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.ruff]
line-length = 88
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 使用方式

```bash
# 格式化代码
uv run black .

# 检查代码风格
uv run ruff check .

# 类型检查
uv run mypy src/
```

---

## 📝 注释规范

### 1. 函数注释
```python
def calculate_score(matches: list[tuple[int, int]], combo: int) -> int:
    """
    计算消除得分
    
    Args:
        matches: 匹配的方块坐标列表
        combo: 连击次数
        
    Returns:
        int: 总得分
        
    Raises:
        ValueError: 当 matches 为空时
    """
    if not matches:
        raise ValueError("matches 不能为空")
    
    base_score = len(matches) * 10
    combo_bonus = combo * 5
    return base_score + combo_bonus
```

### 2. 类注释
```python
class GameBoard:
    """
    游戏棋盘类
    
    管理游戏棋盘状态，包括方块位置、消除逻辑等
    
    Attributes:
        width: 棋盘宽度
        height: 棋盘高度
        board: 二维数组表示棋盘状态
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
```

### 3. 模块注释
```python
"""
游戏核心逻辑模块

提供游戏的核心功能：
- 方块匹配检测
- 消除逻辑
- 重力下落
- 连击计算
"""
```

---

## 🔧 命名规范

### 1. 变量命名
```python
# ✅ 正确：使用描述性名称
user_count = 10
max_retry_attempts = 3
is_game_over = False

# ❌ 错误：使用缩写或单字母
uc = 10
mra = 3
igo = False
```

### 2. 函数命名
```python
# ✅ 正确：动词开头，描述功能
def get_user_by_id(user_id: int) -> User:
    pass

def calculate_total_score(scores: list[int]) -> int:
    pass

def is_valid_move(from_pos: tuple, to_pos: tuple) -> bool:
    pass

# ❌ 错误：不清晰的命名
def user(id: int):
    pass

def score(s: list):
    pass
```

### 3. 类命名
```python
# ✅ 正确：使用名词，PascalCase
class GameEngine:
    pass

class UserManager:
    pass

class DatabaseConnection:
    pass

# ❌ 错误：使用动词或 snake_case
class game_engine:
    pass

class ManageUser:
    pass
```

---

## 🧪 测试规范

### 1. 测试文件命名
```
tests/
├── test_backend.py      # 测试 src/backend/
├── test_core.py         # 测试 src/core/
└── test_utils.py        # 测试 src/utils/
```

### 2. 测试函数命名
```python
def test_calculate_score_with_valid_input():
    """测试：正常输入计算得分"""
    matches = [(0, 0), (0, 1), (0, 2)]
    combo = 1
    score = calculate_score(matches, combo)
    assert score == 35

def test_calculate_score_raises_error_on_empty_matches():
    """测试：空输入抛出异常"""
    with pytest.raises(ValueError):
        calculate_score([], 1)
```

### 3. 测试覆盖率要求
- 最低覆盖率：80%
- 核心业务逻辑：100%
- 工具函数：90%

---

## 📦 项目结构规范

### 标准结构
```
project/
├── src/
│   ├── __init__.py
│   ├── backend/          # 后端服务
│   │   ├── __init__.py
│   │   └── app.py
│   ├── core/             # 核心业务逻辑
│   │   ├── __init__.py
│   │   └── models.py
│   └── utils/            # 工具函数
│       ├── __init__.py
│       └── logger.py
├── tests/                # 测试代码
├── newstandards/         # 开发规范
├── .github/workflows/    # CI/CD 配置
├── pyproject.toml        # 项目配置
├── Dockerfile            # Docker 配置
└── README.md             # 项目文档
```

---

## 🚀 启动命令规范

### 使用 uv run（推荐）
```bash
# ✅ 正确：使用 uv run
uv run python -m src.backend.app
uv run pytest tests/
uv run black .
uv run ruff check .

# ❌ 错误：直接运行
python -m src.backend.app
pytest tests/
```

**原因**:
- `uv run` 自动执行 `uv sync`
- 自动将 `src/` 加入 PYTHONPATH
- 确保依赖正确安装

---

## 🔍 代码审查清单

### 提交前检查
- [ ] 代码格式化（black）
- [ ] 代码风格检查（ruff）
- [ ] 类型检查（mypy）
- [ ] 测试通过（pytest）
- [ ] 测试覆盖率 >= 80%
- [ ] 无 emoji
- [ ] 使用绝对导入
- [ ] 使用 pathlib 处理路径
- [ ] 注释使用简体中文

### CI 自动检查
```yaml
# .github/workflows/ci.yml
- name: 代码格式检查
  run: uv run black --check .

- name: 代码风格检查
  run: uv run ruff check .

- name: 类型检查
  run: uv run mypy src/

- name: 运行测试
  run: uv run pytest tests/ --cov=src --cov-report=term
```

---

## 📚 相关文档

- [02-PROJECT-STRUCTURE.md](02-PROJECT-STRUCTURE.md) - 项目结构规范
- [06-CROSS-PLATFORM-GUIDE.md](06-CROSS-PLATFORM-GUIDE.md) - 跨平台开发指南
- [07-TROUBLESHOOTING.md](07-TROUBLESHOOTING.md) - 常见问题排查

---

**版本**: v3.0  
**更新日期**: 2026-03-28  
**维护者**: 基于实战经验整理
