"""数据探索核心模块。

对外提供数据加载、动态筛选、图表构建与特征洞察能力，
所有模块均不依赖 Streamlit，可独立被测试与复用。
"""

from src.core.data_explorer.charts import PlotlyChartFactory
from src.core.data_explorer.filters import DataFilter, FilterCriteria
from src.core.data_explorer.insights import InsightGenerator, InsightReport
from src.core.data_explorer.loader import CsvDataLoader, DataLoadingError

__all__ = [
    "FilterCriteria",
    "DataFilter",
    "InsightGenerator",
    "InsightReport",
    "CsvDataLoader",
    "DataLoadingError",
    "PlotlyChartFactory",
]
