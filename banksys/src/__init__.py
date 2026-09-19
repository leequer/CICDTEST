"""banksys 源代码根包。

整体分层：
- src.utils：通用工具（日志等）
- src.core.data_explorer：数据探索核心业务逻辑（不依赖 Streamlit）
- src.frontend.dashboard：Streamlit 交互层
"""

__version__ = "0.1.0"
