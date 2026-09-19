"""动态筛选器单元测试。"""

from __future__ import annotations

import pandas as pd

from src.core.data_explorer import schema
from src.core.data_explorer.filters import DataFilter
from src.core.data_explorer.interfaces import DataExplorerError, FilterCriteria


def test_default_criteria_covers_all_fields(sample_dataframe: pd.DataFrame) -> None:
    """测试：默认条件覆盖所有分类字段且数值区间为完整边界。"""
    data_filter = DataFilter()
    criteria = data_filter.default_criteria(sample_dataframe)

    assert "job" in criteria.categorical_selections
    assert schema.TARGET_COLUMN in criteria.categorical_selections
    assert criteria.numeric_ranges["age"] == (24.0, 62.0)


def test_categorical_filter(sample_dataframe: pd.DataFrame) -> None:
    """测试：按职业多选筛选后只剩对应客户。"""
    data_filter = DataFilter()
    criteria = FilterCriteria(
        categorical_selections={"job": ["student"]},
    )
    filtered = data_filter.apply(sample_dataframe, criteria)

    assert len(filtered) == 1
    assert filtered.iloc[0]["job"] == "student"


def test_empty_selection_means_no_limit(sample_dataframe: pd.DataFrame) -> None:
    """测试：分类字段选中空列表表示不限制。"""
    data_filter = DataFilter()
    criteria = FilterCriteria(categorical_selections={"job": []})
    filtered = data_filter.apply(sample_dataframe, criteria)

    assert len(filtered) == len(sample_dataframe)


def test_numeric_range_filter(sample_dataframe: pd.DataFrame) -> None:
    """测试：数值闭区间筛选正确。"""
    data_filter = DataFilter()
    criteria = FilterCriteria(numeric_ranges={"age": (40.0, 60.0)})
    filtered = data_filter.apply(sample_dataframe, criteria)

    assert filtered["age"].between(40, 60).all()
    assert len(filtered) == 3  # 45 / 55 / 41


def test_combined_filters(sample_dataframe: pd.DataFrame) -> None:
    """测试：分类与数值条件联合筛选。"""
    data_filter = DataFilter()
    criteria = FilterCriteria(
        categorical_selections={"contact": ["cellular"]},
        numeric_ranges={"age": (40.0, 200.0)},
    )
    filtered = data_filter.apply(sample_dataframe, criteria)

    assert (filtered["contact"] == "cellular").all()
    assert (filtered["age"] >= 40).all()


def test_unknown_column_raises(sample_dataframe: pd.DataFrame) -> None:
    """测试：引用不存在字段时抛出业务异常。"""
    data_filter = DataFilter()
    criteria = FilterCriteria(categorical_selections={"not_exist": ["x"]})
    try:
        data_filter.apply(sample_dataframe, criteria)
    except DataExplorerError as exc:
        assert "不存在的字段" in str(exc)
    else:
        raise AssertionError("应当抛出 DataExplorerError")


def test_options_follow_business_order(sample_dataframe: pd.DataFrame) -> None:
    """测试：month/day_of_week 等字段按业务顺序而非字母序排列。"""
    data_filter = DataFilter()
    options = data_filter.categorical_options(sample_dataframe)

    assert options["day_of_week"] == ["mon", "tue", "wed", "thu", "fri"]
