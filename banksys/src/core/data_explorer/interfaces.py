"""数据探索模块接口定义（接口先行原则）。

本文件只包含抽象基类、数据契约（dataclass）与异常定义，
不包含任何具体实现，供 loader / filters / charts / insights / 仪表盘共同遵守。

接口契约总览：
- IDataLoader       ：负责从磁盘加载并校验数据集
- IDataFilter       ：负责按筛选条件动态过滤数据
- IChartFactory     ：负责生成 Plotly 图表对象
- IInsightGenerator ：负责生成特征洞察报告
- IDashboardApp     ：负责渲染交互式仪表盘（Streamlit 实现）
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

import pandas as pd


class DatasetName(str, Enum):
    """可选数据集名称。"""

    TRAIN = "train"
    TEST = "test"


class InsightLevel(str, Enum):
    """洞察严重级别（用于前端配色与排序）。"""

    INFO = "info"  # 一般性事实
    SUGGEST = "suggest"  # 特征工程建议
    WARN = "warn"  # 风险提示（如数据泄露、数据质量问题）


class InsightCategory(str, Enum):
    """洞察业务分类。"""

    BUSINESS = "business"  # 业务洞察
    DATA_QUALITY = "quality"  # 数据质量
    FEATURE = "feature"  # 特征工程
    MODELING = "modeling"  # 建模提示


class DataExplorerError(Exception):
    """数据探索模块统一异常基类（中文消息必须面向用户可读）。"""


@dataclass(frozen=True)
class FilterCriteria:
    """动态筛选条件契约。

    Attributes:
        categorical_selections: 分类字段 -> 选中的取值列表；空列表表示“不限制”。
        numeric_ranges: 数值字段 -> (最小值, 最大值) 闭区间；None 表示“不限制”。
    """

    categorical_selections: dict[str, list[str]] = field(default_factory=dict)
    numeric_ranges: dict[str, tuple[float, float]] = field(default_factory=dict)


@dataclass
class DatasetMeta:
    """数据集元信息。

    Attributes:
        name: 数据集名称（train/test）。
        row_count: 样本行数。
        column_count: 字段数量。
        has_target: 是否包含目标列 subscribe。
        positive_count: 正样本（认购）数量，无目标列时为 None。
        negative_count: 负样本数量，无目标列时为 None。
        positive_rate: 正样本比例，无目标列时为 None。
    """

    name: str
    row_count: int
    column_count: int
    has_target: bool
    positive_count: int | None = None
    negative_count: int | None = None
    positive_rate: float | None = None


@dataclass(frozen=True)
class InsightItem:
    """单条特征洞察。

    Attributes:
        title: 洞察标题（简体中文，一句话结论）。
        category: 业务分类。
        level: 严重级别。
        content: 详细说明。
        metrics: 支撑该结论的量化证据，键为中文指标名，值为指标值。
    """

    title: str
    category: InsightCategory
    level: InsightLevel
    content: str
    metrics: dict[str, str] = field(default_factory=dict)


@dataclass
class InsightReport:
    """特征洞察报告。

    Attributes:
        dataset_name: 生成报告所基于的数据集名称。
        row_count: 当前（筛选后）样本量。
        positive_rate: 当前（筛选后）认购率，无目标列时为 None。
        items: 洞察条目列表。
    """

    dataset_name: str
    row_count: int
    positive_rate: float | None
    items: list[InsightItem] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转为可序列化字典（用于 JSON 导出）。"""
        return {
            "dataset_name": self.dataset_name,
            "row_count": self.row_count,
            "positive_rate": self.positive_rate,
            "items": [
                {
                    "title": item.title,
                    "category": item.category.value,
                    "level": item.level.value,
                    "content": item.content,
                    "metrics": item.metrics,
                }
                for item in self.items
            ],
        }


class IDataLoader(ABC):
    """数据加载器接口。"""

    @abstractmethod
    def load(self, dataset: DatasetName | str) -> pd.DataFrame:
        """加载指定数据集。

        Args:
            dataset: 数据集名称（DatasetName 枚举或字符串 train/test）。

        Returns:
            pd.DataFrame: 按字段字典完成类型校正的数据表。

        Raises:
            DataLoadingError: 文件不存在或字段缺失/不匹配时抛出。
        """
        raise NotImplementedError

    @abstractmethod
    def describe(self, dataset: DatasetName | str) -> DatasetMeta:
        """返回数据集元信息（行数、列数、目标分布）。"""
        raise NotImplementedError


class IDataFilter(ABC):
    """动态筛选器接口。"""

    @abstractmethod
    def apply(self, data: pd.DataFrame, criteria: FilterCriteria) -> pd.DataFrame:
        """按筛选条件返回过滤后的数据副本。

        Raises:
            DataExplorerError: 条件引用了不存在的字段时抛出。
        """
        raise NotImplementedError

    @abstractmethod
    def default_criteria(self, data: pd.DataFrame) -> FilterCriteria:
        """根据数据实际取值生成“不限制任何字段”的默认条件。"""
        raise NotImplementedError

    @abstractmethod
    def categorical_options(self, data: pd.DataFrame) -> dict[str, list[str]]:
        """返回各分类字段的可选值（含业务顺序排列）。"""
        raise NotImplementedError

    @abstractmethod
    def numeric_bounds(self, data: pd.DataFrame) -> dict[str, tuple[float, float]]:
        """返回各数值字段的最小/最大值边界。"""
        raise NotImplementedError


class IChartFactory(ABC):
    """图表工厂接口（全部返回 plotly Figure，不做前端渲染）。"""

    @abstractmethod
    def target_distribution(self, data: pd.DataFrame) -> "object":
        """目标变量 subscribe 分布图（柱状 + 认购率标注）。"""
        raise NotImplementedError

    @abstractmethod
    def categorical_distribution(
        self, data: pd.DataFrame, column: str, group_by_target: bool = False
    ) -> "object":
        """分类字段分布图；group_by_target 为 True 时按认购结果分组着色。"""
        raise NotImplementedError

    @abstractmethod
    def numeric_distribution(
        self, data: pd.DataFrame, column: str, group_by_target: bool = False
    ) -> "object":
        """数值字段分布直方图；group_by_target 为 True 时按认购结果分组。"""
        raise NotImplementedError

    @abstractmethod
    def subscribe_rate_by_category(self, data: pd.DataFrame, column: str) -> "object":
        """分类字段各取值的认购率对比柱状图。"""
        raise NotImplementedError

    @abstractmethod
    def subscribe_rate_by_numeric(
        self, data: pd.DataFrame, column: str, bins: int = 8
    ) -> "object":
        """数值字段分箱后各箱认购率折线图。"""
        raise NotImplementedError

    @abstractmethod
    def correlation_heatmap(self, data: pd.DataFrame) -> "object":
        """数值字段（含认购标签编码）相关性热图。"""
        raise NotImplementedError

    @abstractmethod
    def missing_value_overview(self, data: pd.DataFrame) -> "object":
        """各字段缺失/unknown 占比柱状图。"""
        raise NotImplementedError


class IInsightGenerator(ABC):
    """特征洞察生成器接口。"""

    @abstractmethod
    def generate(
        self, data: pd.DataFrame, dataset_name: str = "train"
    ) -> InsightReport:
        """基于给定数据（通常是筛选后数据）生成特征洞察报告。"""
        raise NotImplementedError


class IDashboardApp(ABC):
    """仪表盘应用接口。"""

    @abstractmethod
    def render(self) -> None:
        """渲染整个仪表盘页面（仅在 Streamlit 运行时上下文中调用）。"""
        raise NotImplementedError
