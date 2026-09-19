"""图表工厂单元测试。"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.core.data_explorer.charts import PlotlyChartFactory
from src.core.data_explorer.interfaces import DataExplorerError


@pytest.fixture
def factory() -> PlotlyChartFactory:
    """测试用图表工厂。"""
    return PlotlyChartFactory()


def test_target_distribution_returns_figure(
    factory: PlotlyChartFactory, sample_dataframe: pd.DataFrame
) -> None:
    """测试：目标分布图返回带数据的 Figure。"""
    figure = factory.target_distribution(sample_dataframe)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) >= 1


def test_categorical_and_numeric_distribution(
    factory: PlotlyChartFactory, sample_dataframe: pd.DataFrame
) -> None:
    """测试：分类/数值分布图均可生成且支持按标签分组。"""
    cat_figure = factory.categorical_distribution(
        sample_dataframe, "job", group_by_target=True
    )
    num_figure = factory.numeric_distribution(
        sample_dataframe, "age", group_by_target=True
    )
    assert isinstance(cat_figure, go.Figure)
    assert isinstance(num_figure, go.Figure)
    assert len(cat_figure.data) >= 2  # 按 yes/no 分组至少两个轨迹


def test_subscribe_rate_charts(
    factory: PlotlyChartFactory, sample_dataframe: pd.DataFrame
) -> None:
    """测试：分类与数值认购率图返回图形。"""
    cat_figure = factory.subscribe_rate_by_category(sample_dataframe, "month")
    num_figure = factory.subscribe_rate_by_numeric(sample_dataframe, "duration", bins=4)
    assert len(cat_figure.data[0].x) > 0
    assert len(num_figure.data[0].x) > 0


def test_correlation_heatmap(
    factory: PlotlyChartFactory, sample_dataframe: pd.DataFrame
) -> None:
    """测试：相关性热图包含标签编码维度。"""
    figure = factory.correlation_heatmap(sample_dataframe)
    # imshow 的坐标标签位于数据轨迹的 x 数组中
    x_labels = list(figure.data[0].x)
    assert "subscribe_编码" in x_labels


def test_missing_value_overview(
    factory: PlotlyChartFactory, sample_dataframe: pd.DataFrame
) -> None:
    """测试：数据质量图能识别 unknown 字段。"""
    figure = factory.missing_value_overview(sample_dataframe)
    assert isinstance(figure, go.Figure)


def test_target_charts_forbid_test_set(
    factory: PlotlyChartFactory, sample_test_dataframe: pd.DataFrame
) -> None:
    """测试：无标签数据调用认购类图表时抛出中文异常。"""
    with pytest.raises(DataExplorerError, match="不含 subscribe 目标列"):
        factory.subscribe_rate_by_category(sample_test_dataframe, "job")


def test_empty_dataframe_returns_empty_figure(
    factory: PlotlyChartFactory, sample_dataframe: pd.DataFrame
) -> None:
    """测试：空数据返回无数据提示图而不是报错。"""
    empty = sample_dataframe.iloc[0:0]
    figure = factory.target_distribution(empty)
    assert isinstance(figure, go.Figure)
