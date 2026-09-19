"""统一日志模块。

基于 rich 实现简体中文彩色日志，全项目必须通过 get_logger 获取日志器。

颜色规定（全项目统一，不得自行更改）：
- DEBUG   : dim            暗白色（调试细节）
- INFO    : cyan           青色（正常流程信息）
- SUCCESS : bold green     加粗绿色（业务成功，自定义级别 25）
- WARNING : yellow         黄色（警告但流程可继续）
- ERROR   : red            红色（业务错误）
- CRITICAL: bold white on red  加粗白字红底（致命错误）
"""

from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

# 全局唯一控制台，供需要直接打印富文本的模块复用
console = Console()

# 自定义成功级别（介于 INFO=20 与 WARNING=30 之间）
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


def _success(
    self: logging.Logger, message: str, *args: object, **kwargs: object
) -> None:
    """以 SUCCESS 级别输出日志。"""
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


# 为标准 Logger 注入 success 方法
logging.Logger.success = _success  # type: ignore[attr-defined]


class _ChineseRichHandler(RichHandler):
    """固定中文输出风格的 Rich 日志处理器。"""

    def __init__(self) -> None:
        super().__init__(
            console=console,
            show_path=True,
            rich_tracebacks=True,
            log_time_format="[%Y-%m-%d %H:%M:%S]",
            markup=True,
        )


# 各级别统一颜色前缀（rich markup）
_STYLE_PREFIX = {
    logging.DEBUG: "[dim]",
    logging.INFO: "[cyan]",
    SUCCESS_LEVEL: "[bold green]",
    logging.WARNING: "[yellow]",
    logging.ERROR: "[red]",
    logging.CRITICAL: "[bold white on red]",
}
_STYLE_SUFFIX = "[/]"


class _ColorFormatter(logging.Formatter):
    """为日志消息按级别包裹规定颜色的格式化器。"""

    def format(self, record: logging.LogRecord) -> str:
        original = record.getMessage()
        prefix = _STYLE_PREFIX.get(record.levelno, "")
        record.msg = f"{prefix}{original}{_STYLE_SUFFIX}"
        record.args = ()
        try:
            return super().format(record)
        finally:
            # 还原记录，避免同一记录被重复处理时嵌套标签
            record.msg = original


def setup_logger(name: str = "banksys", level: int = logging.INFO) -> logging.Logger:
    """创建或获取带 rich 彩色输出的日志器。

    重复调用同名日志器不会叠加处理器。

    Args:
        name: 日志器名称，通常传 __name__ 或固定业务名。
        level: 日志级别，默认 INFO。

    Returns:
        logging.Logger: 配置完成的日志器。
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = _ChineseRichHandler()
        handler.setFormatter(_ColorFormatter())
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger


def get_logger(name: str = "banksys") -> logging.Logger:
    """获取项目统一日志器（setup_logger 的语义化别名）。"""
    return setup_logger(name)


def get_project_root() -> Path:
    """获取项目根目录（banksys/）。

    当前文件位于 src/utils/logger.py，向上三级即项目根。
    """
    return Path(__file__).resolve().parents[2]
