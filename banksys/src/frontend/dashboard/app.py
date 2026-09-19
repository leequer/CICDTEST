"""银行营销数据探索交互式仪表盘（Streamlit 入口）。

本地启动方式（在项目根目录 banksys/ 下）：
    envbank\\Scripts\\streamlit run src\\frontend\\dashboard\\app.py

设计原则：
- 页面控件只负责收集用户输入，业务逻辑全部下沉到 src.core.data_explorer；
- 全部界面文案、注释均为简体中文，不使用 emoji。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# 兼容 `streamlit run` 直接启动：把项目根目录加入模块搜索路径，保证绝对导入可用
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.core.data_explorer import schema
from src.core.data_explorer.charts import PlotlyChartFactory
from src.core.data_explorer.filters import DataFilter
from src.core.data_explorer.insights import InsightGenerator
from src.core.data_explorer.interfaces import (
    DataExplorerError,
    FilterCriteria,
    InsightLevel,
)
from src.core.data_explorer.loader import CsvDataLoader
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 洞察级别对应的界面配色（与 rich 日志颜色体系语义保持一致）
_LEVEL_LABEL = {
    InsightLevel.INFO: "信息",
    InsightLevel.SUGGEST: "建议",
    InsightLevel.WARN: "风险提示",
}
_LEVEL_COLOR = {
    InsightLevel.INFO: "#4C78A8",
    InsightLevel.SUGGEST: "#F58518",
    InsightLevel.WARN: "#E45756",
}
_LEVEL_CATEGORY_LABEL = {
    "business": "业务洞察",
    "quality": "数据质量",
    "feature": "特征工程",
    "modeling": "建模提示",
}


@st.cache_resource
def _get_loader() -> CsvDataLoader:
    """获取全局唯一的数据加载器（缓存资源）。"""
    return CsvDataLoader()


@st.cache_data(show_spinner="正在加载数据，请稍候……")
def _load_dataset(dataset_name: str) -> pd.DataFrame:
    """通过 Streamlit 缓存加载数据集，避免每次交互都重新读盘。"""
    logger.info("仪表盘请求加载数据集：%s", dataset_name)
    return _get_loader().load(dataset_name)


def _chinese_field_name(column: str) -> str:
    """返回“中文名（英文字段名）”形式的展示名。"""
    chinese_name = schema.COLUMN_DESCRIPTIONS.get(column, (column, ""))[0]
    return f"{chinese_name}（{column}）"


def _render_sidebar_filters(
    data: pd.DataFrame, data_filter: DataFilter
) -> FilterCriteria:
    """在侧边栏渲染所有字段的动态筛选控件，返回 FilterCriteria。"""
    st.sidebar.header("一、数据集选择")
    dataset_name = st.sidebar.radio(
        "选择数据集",
        options=["train", "test"],
        format_func=lambda value: (
            "训练集 train.csv（含认购标签）"
            if value == "train"
            else "测试集 test.csv（无标签）"
        ),
        index=0,
    )

    st.sidebar.header("二、动态筛选条件")
    if st.sidebar.button("重置全部筛选条件", width="stretch"):
        for key in list(st.session_state.keys()):
            if key.startswith("filter_"):
                del st.session_state[key]
        st.rerun()

    options = data_filter.categorical_options(data)
    bounds = data_filter.numeric_bounds(data)

    categorical_selections: dict[str, list[str]] = {}
    numeric_ranges: dict[str, tuple[float, float]] = {}

    st.sidebar.caption("分类字段（多选，默认全选）")
    for column, values in options.items():
        selected = st.sidebar.multiselect(
            _chinese_field_name(column),
            options=values,
            default=values,
            key=f"filter_cat_{column}",
        )
        categorical_selections[column] = selected

    st.sidebar.caption("数值字段（区间滑块）")
    for column, (lower_bound, upper_bound) in bounds.items():
        if column == "pdays":
            st.sidebar.caption("提示：pdays=999 表示此前从未联系过该客户")
        # 注意：min/max/value 均为 float，step 也必须是 float，否则 Streamlit 报类型错误
        step = 1.0 if float(upper_bound).is_integer() else 0.1
        selected_range = st.sidebar.slider(
            _chinese_field_name(column),
            min_value=lower_bound,
            max_value=upper_bound,
            value=(lower_bound, upper_bound),
            step=step,
            key=f"filter_num_{column}",
        )
        numeric_ranges[column] = (float(selected_range[0]), float(selected_range[1]))

    criteria = FilterCriteria(
        categorical_selections=categorical_selections,
        numeric_ranges=numeric_ranges,
    )
    return dataset_name, criteria


def _render_overview(
    data: pd.DataFrame, filtered: pd.DataFrame, factory: PlotlyChartFactory
) -> None:
    """渲染“数据概览”页签。"""
    st.subheader("数据概览")

    meta = _get_loader().describe(st.session_state["dataset_name"])
    column_meta_1, column_meta_2, column_meta_3 = st.columns(3)
    column_meta_1.metric("数据集", meta.name)
    column_meta_2.metric("原始样本量", f"{meta.row_count:,} 行")
    column_meta_3.metric("字段数量", f"{meta.column_count} 列")

    if schema.TARGET_COLUMN in data.columns:
        st.plotly_chart(factory.target_distribution(filtered), width="stretch")
    else:
        st.info(
            "测试集不包含 subscribe 目标列，因此本页仅展示字段与数据质量分布，"
            "认购相关分析请切换至训练集。"
        )

    st.plotly_chart(factory.missing_value_overview(filtered), width="stretch")

    st.markdown("#### 字段数据字典")
    dictionary_rows = [
        {"英文字段名": column, "中文名": chinese_name, "业务含义": description}
        for column, (chinese_name, description) in schema.COLUMN_DESCRIPTIONS.items()
        if column in data.columns
    ]
    st.dataframe(pd.DataFrame(dictionary_rows), width="stretch", hide_index=True)

    st.markdown("#### 筛选后明细数据（最多预览前 500 行）")
    st.dataframe(filtered.head(500), width="stretch")


def _render_distribution(
    data: pd.DataFrame, filtered: pd.DataFrame, factory: PlotlyChartFactory
) -> None:
    """渲染“字段分布分析”页签。"""
    st.subheader("字段分布分析")

    has_target = schema.TARGET_COLUMN in data.columns
    group_by_target = st.checkbox(
        "按认购结果分组着色（仅训练集）", value=False, disabled=not has_target
    )
    if not has_target and group_by_target:
        group_by_target = False

    all_fields = list(schema.CATEGORICAL_COLUMNS) + list(schema.NUMERIC_COLUMNS)
    all_fields = [column for column in all_fields if column in data.columns]
    selected_column = st.selectbox(
        "选择要分析的字段",
        options=all_fields,
        format_func=_chinese_field_name,
    )

    if selected_column in schema.CATEGORICAL_COLUMNS:
        figure = factory.categorical_distribution(
            filtered, selected_column, group_by_target=group_by_target
        )
    else:
        figure = factory.numeric_distribution(
            filtered, selected_column, group_by_target=group_by_target
        )
    st.plotly_chart(figure, width="stretch")


def _render_correlation(filtered: pd.DataFrame, factory: PlotlyChartFactory) -> None:
    """渲染“相关性分析”页签。"""
    st.subheader("数值特征相关性分析")
    st.caption(
        "热图展示数值字段之间的皮尔逊相关系数；训练集额外包含 subscribe 编码列，"
        "可观察各特征与认购结果的线性相关性。"
    )
    st.plotly_chart(factory.correlation_heatmap(filtered), width="stretch")


def _render_subscribe_compare(
    data: pd.DataFrame, filtered: pd.DataFrame, factory: PlotlyChartFactory
) -> None:
    """渲染“认购率分组对比”页签。"""
    st.subheader("按字段对比各组认购率")
    if schema.TARGET_COLUMN not in data.columns:
        st.warning(
            "测试集无 subscribe 标签，无法进行认购率对比，请在左侧切换到训练集。"
        )
        return

    analysis_type = st.radio(
        "字段类型",
        options=["分类字段", "数值字段"],
        horizontal=True,
    )
    if analysis_type == "分类字段":
        candidates = [
            column for column in schema.CATEGORICAL_COLUMNS if column in data.columns
        ]
        selected_column = st.selectbox(
            "选择分类字段",
            options=candidates,
            format_func=_chinese_field_name,
        )
        st.plotly_chart(
            factory.subscribe_rate_by_category(filtered, selected_column),
            width="stretch",
        )
    else:
        candidates = [
            column for column in schema.NUMERIC_COLUMNS if column in data.columns
        ]
        selected_column = st.selectbox(
            "选择数值字段",
            options=candidates,
            format_func=_chinese_field_name,
        )
        bins = st.slider("分档数量", min_value=3, max_value=10, value=8)
        st.plotly_chart(
            factory.subscribe_rate_by_numeric(filtered, selected_column, bins=bins),
            width="stretch",
        )


def _render_insights(
    data: pd.DataFrame,
    filtered: pd.DataFrame,
    dataset_name: str,
    generator: InsightGenerator,
) -> None:
    """渲染“特征洞察报告”页签。"""
    st.subheader("特征洞察报告")
    report = generator.generate(filtered, dataset_name=dataset_name)

    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("分析样本量", f"{report.row_count:,} 行")
    if report.positive_rate is not None:
        metric_2.metric("当前认购率", f"{report.positive_rate:.2%}")
    else:
        metric_2.metric("当前认购率", "无标签")
    metric_3.metric("洞察条目数", f"{len(report.items)} 条")

    if not report.items:
        st.info("当前数据没有可生成的洞察。")
        return

    for item in report.items:
        level = item.level
        color = _LEVEL_COLOR[level]
        category_label = _LEVEL_CATEGORY_LABEL.get(
            item.category.value, item.category.value
        )
        level_label = _LEVEL_LABEL[level]
        st.markdown(
            f"""
            <div style="border-left:5px solid {color};padding:10px 14px;
                        background:#f7f8fa;margin-bottom:10px;">
                <strong style="color:{color};">[{level_label}]</strong>
                <span style="color:#888888;">{category_label}</span>
                <div style="font-size:16px;margin-top:4px;">{item.title}</div>
                <div style="color:#444444;margin-top:4px;">{item.content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if item.metrics:
            with st.expander("查看量化证据", expanded=False):
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"指标": key, "数值": value}
                            for key, value in item.metrics.items()
                        ]
                    ),
                    width="stretch",
                    hide_index=True,
                )

    st.download_button(
        label="导出洞察报告（JSON）",
        data=json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        file_name=f"banksys_insights_{dataset_name}.json",
        mime="application/json",
    )


def render() -> None:
    """渲染整个仪表盘（由 IDashboardApp 契约约束，main 脚本直接调用）。"""
    st.set_page_config(
        page_title="银行营销数据探索仪表盘 - banksys",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("银行电话营销数据探索仪表盘")
    st.caption(
        "场景：通过历史客户数据理解定期存款认购规律，为精准营销提供数据依据。"
        "可在左侧对全部字段进行动态筛选，所有图表与洞察会随筛选实时更新。"
    )

    data_filter = DataFilter()

    # 侧边栏同时承担数据集选择，需要先拿到数据集再构建筛选控件
    # 第一次渲染时默认 train，后续以 session_state 保持选择
    preselected = st.session_state.get("dataset_name", "train")
    placeholder_data = _load_dataset(preselected)

    st.sidebar.title("筛选与设置")
    dataset_name, criteria = _render_sidebar_filters(placeholder_data, data_filter)
    st.session_state["dataset_name"] = dataset_name

    # 用户切换数据集后重新加载并重建控件
    if dataset_name != preselected:
        st.rerun()

    data = _load_dataset(dataset_name)
    try:
        filtered = data_filter.apply(data, criteria)
    except DataExplorerError as exc:
        st.error(f"筛选失败：{exc}")
        return

    # 顶部关键指标
    total_count = len(data)
    filtered_count = len(filtered)
    kpi_columns = st.columns(4)
    kpi_columns[0].metric("原始样本量", f"{total_count:,}")
    kpi_columns[1].metric("筛选后样本量", f"{filtered_count:,}")
    keep_ratio = filtered_count / total_count if total_count else 0.0
    kpi_columns[2].metric("样本保留比例", f"{keep_ratio:.2%}")
    if schema.TARGET_COLUMN in data.columns and filtered_count:
        positive_count = int(
            (filtered[schema.TARGET_COLUMN] == schema.POSITIVE_LABEL).sum()
        )
        kpi_columns[3].metric(
            "筛选后认购率",
            f"{positive_count / filtered_count:.2%}",
            delta=f"认购 {positive_count:,} 人",
        )
    else:
        kpi_columns[3].metric("筛选后认购率", "无标签" if total_count else "-")

    factory = PlotlyChartFactory()
    generator = InsightGenerator()

    tab_overview, tab_distribution, tab_correlation, tab_compare, tab_insights = (
        st.tabs(
            ["数据概览", "字段分布分析", "相关性分析", "认购率分组对比", "特征洞察报告"]
        )
    )
    with tab_overview:
        _render_overview(data, filtered, factory)
    with tab_distribution:
        _render_distribution(data, filtered, factory)
    with tab_correlation:
        _render_correlation(filtered, factory)
    with tab_compare:
        _render_subscribe_compare(data, filtered, factory)
    with tab_insights:
        _render_insights(data, filtered, dataset_name, generator)


if __name__ == "__main__":
    render()
