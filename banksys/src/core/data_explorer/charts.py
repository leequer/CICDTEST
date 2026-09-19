"""Plotly 图表工厂实现。

所有方法均返回 plotly Figure 对象，不感知任何前端框架，
便于在 Streamlit / 导出报告 / 单元测试中复用。

配色约定：
- 未认购 no : 柔和蓝色 #4C78A8
- 认购 yes  : 醒目橙红 #F58518
- 相关性热图: Reds 色系
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.core.data_explorer import schema
from src.core.data_explorer.interfaces import (
    DataExplorerError,
    IChartFactory,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 目标变量统一配色
TARGET_COLOR_MAP = {schema.NEGATIVE_LABEL: "#4C78A8", schema.POSITIVE_LABEL: "#F58518"}
TARGET_NAME_MAP = {schema.NEGATIVE_LABEL: "未认购", schema.POSITIVE_LABEL: "认购"}

# 全局图表模板
_CHART_TEMPLATE = "plotly_white"


def _apply_common_style(fig: go.Figure, title: str) -> go.Figure:
    """统一应用中文字体、标题、留白等样式。"""
    fig.update_layout(
        title=title,
        template=_CHART_TEMPLATE,
        title_font_size=18,
        margin={"l": 40, "r": 40, "t": 60, "b": 40},
        legend_title_text="",
    )
    return fig


def _empty_figure(title: str) -> go.Figure:
    """构造无数据提示图。"""
    fig = go.Figure()
    fig.add_annotation(
        text="当前筛选条件下没有可展示的样本",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 16, "color": "#888888"},
    )
    return _apply_common_style(fig, title)


def _ensure_target(data: pd.DataFrame) -> None:
    """确认目标列存在（test 集无标签时给出明确中文提示）。"""
    if schema.TARGET_COLUMN not in data.columns:
        message = (
            "当前数据集不含 subscribe 目标列（测试集无标签），无法进行认购相关分析"
        )
        logger.warning(message)
        raise DataExplorerError(message)


class PlotlyChartFactory(IChartFactory):
    """基于 Plotly Express 的图表工厂。"""

    def target_distribution(self, data: pd.DataFrame) -> go.Figure:
        """目标变量分布柱状图，标注数量与整体认购率。"""
        title = "目标变量分布：客户是否认购定期存款"
        _ensure_target(data)
        if data.empty:
            return _empty_figure(title)

        counts = (
            data[schema.TARGET_COLUMN]
            .value_counts()
            .reindex([schema.NEGATIVE_LABEL, schema.POSITIVE_LABEL])
            .fillna(0)
            .astype(int)
        )
        total = int(counts.sum())
        chart_data = pd.DataFrame(
            {
                "认购结果": [TARGET_NAME_MAP[label] for label in counts.index],
                "客户数": counts.values,
            }
        )
        fig = px.bar(
            chart_data,
            x="认购结果",
            y="客户数",
            color="认购结果",
            color_discrete_map={
                "未认购": TARGET_COLOR_MAP[schema.NEGATIVE_LABEL],
                "认购": TARGET_COLOR_MAP[schema.POSITIVE_LABEL],
            },
            text="客户数",
        )
        positive_rate = counts[schema.POSITIVE_LABEL] / total if total else 0.0
        fig.update_traces(textposition="outside", width=0.5)
        return _apply_common_style(
            fig, f"{title}（整体认购率 {positive_rate:.2%}，样本 {total} 人）"
        )

    def categorical_distribution(
        self, data: pd.DataFrame, column: str, group_by_target: bool = False
    ) -> go.Figure:
        """分类字段分布柱状图，可按认购结果分组着色。"""
        chinese_name = schema.COLUMN_DESCRIPTIONS.get(column, (column, ""))[0]
        title = f"分类字段分布：{chinese_name}（{column}）"
        if data.empty or column not in data.columns:
            return _empty_figure(title)

        category_orders = {}
        ordered = schema.ORDERED_CATEGORIES.get(column)
        if ordered is not None:
            category_orders[column] = list(ordered)

        if group_by_target:
            _ensure_target(data)
            plot_data = data.rename(columns={schema.TARGET_COLUMN: "认购结果"})
            plot_data["认购结果"] = plot_data["认购结果"].map(TARGET_NAME_MAP)
            fig = px.histogram(
                plot_data,
                x=column,
                color="认购结果",
                barmode="group",
                category_orders=category_orders,
                color_discrete_map={
                    "未认购": TARGET_COLOR_MAP[schema.NEGATIVE_LABEL],
                    "认购": TARGET_COLOR_MAP[schema.POSITIVE_LABEL],
                },
            )
            fig.update_yaxes(title_text="客户数")
        else:
            counts = data[column].value_counts()
            if ordered is not None:
                present = [value for value in ordered if value in counts.index]
                counts = counts.reindex(
                    present + sorted(set(counts.index) - set(present))
                )
            chart_data = pd.DataFrame({column: counts.index, "客户数": counts.values})
            fig = px.bar(chart_data, x=column, y="客户数", text="客户数")
            fig.update_traces(textposition="outside")
            fig.update_yaxes(title_text="客户数")
            if category_orders:
                fig.update_xaxes(
                    categoryorder="array", categoryarray=category_orders[column]
                )

        fig.update_xaxes(title_text=chinese_name)
        return _apply_common_style(fig, title)

    def numeric_distribution(
        self, data: pd.DataFrame, column: str, group_by_target: bool = False
    ) -> go.Figure:
        """数值字段分布直方图，可按认购结果分组。"""
        chinese_name = schema.COLUMN_DESCRIPTIONS.get(column, (column, ""))[0]
        title = f"数值字段分布：{chinese_name}（{column}）"
        if data.empty or column not in data.columns:
            return _empty_figure(title)

        plot_data = data.dropna(subset=[column])
        if group_by_target:
            _ensure_target(plot_data)
            plot_data = plot_data.rename(columns={schema.TARGET_COLUMN: "认购结果"})
            plot_data["认购结果"] = plot_data["认购结果"].map(TARGET_NAME_MAP)
            fig = px.histogram(
                plot_data,
                x=column,
                color="认购结果",
                barmode="overlay",
                nbins=40,
                opacity=0.65,
                color_discrete_map={
                    "未认购": TARGET_COLOR_MAP[schema.NEGATIVE_LABEL],
                    "认购": TARGET_COLOR_MAP[schema.POSITIVE_LABEL],
                },
            )
        else:
            fig = px.histogram(
                plot_data, x=column, nbins=40, color_discrete_sequence=["#4C78A8"]
            )
        fig.update_xaxes(title_text=chinese_name)
        fig.update_yaxes(title_text="客户数")
        return _apply_common_style(fig, title)

    def subscribe_rate_by_category(self, data: pd.DataFrame, column: str) -> go.Figure:
        """分类字段各取值的认购率对比图（柱高=认购率，悬停看样本数）。"""
        chinese_name = schema.COLUMN_DESCRIPTIONS.get(column, (column, ""))[0]
        title = f"分组认购率对比：{chinese_name}（{column}）"
        _ensure_target(data)
        if data.empty or column not in data.columns:
            return _empty_figure(title)

        grouped = (
            data.groupby(column)[schema.TARGET_COLUMN]
            .agg(
                样本数="count",
                认购数=lambda series: int((series == schema.POSITIVE_LABEL).sum()),
            )
            .reset_index()
        )
        grouped["认购率"] = grouped["认购数"] / grouped["样本数"]

        ordered = schema.ORDERED_CATEGORIES.get(column)
        if ordered is not None:
            order_map = {value: index for index, value in enumerate(ordered)}
            grouped = grouped.sort_values(
                by=column,
                key=lambda series: series.map(lambda value: order_map.get(value, 999)),
            )
        else:
            grouped = grouped.sort_values(by="认购率", ascending=False)

        fig = px.bar(
            grouped,
            x=column,
            y="认购率",
            text=grouped["认购率"].map(lambda value: f"{value:.1%}"),
            custom_data=["样本数", "认购数"],
            color="认购率",
            color_continuous_scale=["#4C78A8", "#F58518"],
        )
        fig.update_traces(
            hovertemplate="%{x}<br>认购率：%{y:.2%}<br>样本数：%{customdata[0]}<extra></extra>",
            textposition="outside",
        )
        fig.update_yaxes(title_text="认购率", tickformat=".0%", range=[0, 1.05])
        fig.update_xaxes(title_text=chinese_name)
        fig.update_layout(coloraxis_showscale=False)
        return _apply_common_style(fig, title)

    def subscribe_rate_by_numeric(
        self, data: pd.DataFrame, column: str, bins: int = 8
    ) -> go.Figure:
        """数值字段等频分箱后的认购率折线图。"""
        chinese_name = schema.COLUMN_DESCRIPTIONS.get(column, (column, ""))[0]
        title = f"分箱认购率趋势：{chinese_name}（{column}，{bins} 档）"
        _ensure_target(data)
        if data.empty or column not in data.columns:
            return _empty_figure(title)

        plot_data = data.dropna(subset=[column]).copy()
        if plot_data[column].nunique() <= bins:
            # 离散度很低时直接按取值分组，避免无意义分箱
            plot_data["分箱"] = plot_data[column].astype(str)
            grouped = plot_data.groupby("分箱", sort=False)[schema.TARGET_COLUMN].agg(
                样本数="count",
                认购率=lambda series: float((series == schema.POSITIVE_LABEL).mean()),
            )
            x_values = grouped.index.tolist()
        else:
            plot_data["分箱"] = pd.qcut(
                plot_data[column],
                q=min(bins, plot_data[column].nunique()),
                duplicates="drop",
            )
            grouped = plot_data.groupby("分箱", observed=True)[
                schema.TARGET_COLUMN
            ].agg(
                样本数="count",
                认购率=lambda series: float((series == schema.POSITIVE_LABEL).mean()),
            )
            x_values = [str(interval) for interval in grouped.index]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=grouped["认购率"].tolist(),
                mode="lines+markers+text",
                line={"color": "#F58518", "width": 3},
                marker={"size": 10},
                text=[f"{value:.1%}" for value in grouped["认购率"]],
                textposition="top center",
                customdata=grouped["样本数"].tolist(),
                hovertemplate=(
                    "区间 %{x}<br>认购率：%{y:.2%}"
                    "<br>样本数：%{customdata}<extra></extra>"
                ),
            )
        )
        fig.update_yaxes(title_text="认购率", tickformat=".0%", range=[0, 1.05])
        fig.update_xaxes(title_text=f"{chinese_name}区间")
        return _apply_common_style(fig, title)

    def correlation_heatmap(self, data: pd.DataFrame) -> go.Figure:
        """数值字段相关性热图（目标列按 yes=1 编码后纳入）。"""
        title = "数值特征相关性热图（含认购标签编码）"
        numeric_columns = [
            column for column in schema.NUMERIC_COLUMNS if column in data.columns
        ]
        plot_data = data[numeric_columns].copy()
        if schema.TARGET_COLUMN in data.columns:
            plot_data["subscribe_编码"] = (
                data[schema.TARGET_COLUMN].map({schema.POSITIVE_LABEL: 1}).fillna(0)
            )
        if plot_data.shape[1] < 2 or data.empty:
            return _empty_figure(title)

        correlation = plot_data.corr(numeric_only=True).round(3)
        fig = px.imshow(
            correlation,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
        )
        fig.update_coloraxes(colorbar_title="相关系数")
        return _apply_common_style(fig, title)

    def missing_value_overview(self, data: pd.DataFrame) -> go.Figure:
        """各字段缺失情况柱状图：分类字段统计 unknown，数值字段统计空值。"""
        title = "数据质量概览：缺失 / unknown 占比"
        if data.empty:
            return _empty_figure(title)

        rows = []
        total_rows = len(data)
        for column in schema.CATEGORICAL_COLUMNS:
            if column in data.columns:
                missing = int((data[column] == schema.UNKNOWN_TOKEN).sum())
                rows.append((column, missing / total_rows, missing))
        for column in schema.NUMERIC_COLUMNS:
            if column in data.columns:
                missing = int(pd.to_numeric(data[column], errors="coerce").isna().sum())
                rows.append((column, missing / total_rows, missing))

        chart_data = pd.DataFrame(rows, columns=["字段", "缺失占比", "缺失数量"])
        chart_data = chart_data.sort_values(by="缺失占比", ascending=False)
        fig = px.bar(
            chart_data,
            x="字段",
            y="缺失占比",
            text=chart_data["缺失占比"].map(lambda value: f"{value:.1%}"),
            custom_data=["缺失数量"],
            color="缺失占比",
            color_continuous_scale=["#4C78A8", "#E45756"],
        )
        fig.update_traces(
            hovertemplate=(
                "字段 %{x}<br>占比：%{y:.2%}"
                "<br>数量：%{customdata[0]}<extra></extra>"
            )
        )
        fig.update_yaxes(title_text="缺失占比", tickformat=".0%")
        fig.update_layout(coloraxis_showscale=False)
        return _apply_common_style(fig, title)
