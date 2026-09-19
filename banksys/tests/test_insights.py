"""特征洞察生成器单元测试。"""

from __future__ import annotations

import pandas as pd

from src.core.data_explorer.insights import InsightGenerator
from src.core.data_explorer.interfaces import InsightCategory, InsightLevel


def test_report_basic_metrics(sample_dataframe: pd.DataFrame) -> None:
    """测试：报告汇总指标正确。"""
    generator = InsightGenerator()
    report = generator.generate(sample_dataframe, dataset_name="train")

    assert report.row_count == 8
    assert report.positive_rate == 0.375
    assert len(report.items) >= 4


def test_report_contains_duration_leakage_warning(
    sample_dataframe: pd.DataFrame,
) -> None:
    """测试：报告必须包含 duration 数据泄露红线提示。"""
    generator = InsightGenerator()
    report = generator.generate(sample_dataframe)

    titles = " ".join(item.title for item in report.items)
    assert "duration" in titles
    warning = next(
        item
        for item in report.items
        if item.level == InsightLevel.WARN and "duration" in item.title
    )
    assert warning.category == InsightCategory.MODELING


def test_report_contains_pdays_quality_note(sample_dataframe: pd.DataFrame) -> None:
    """测试：报告包含 pdays=999 数据质量说明。"""
    generator = InsightGenerator()
    report = generator.generate(sample_dataframe)

    assert any("pdays" in item.title for item in report.items)


def test_report_for_unlabeled_test_set(sample_test_dataframe: pd.DataFrame) -> None:
    """测试：无标签数据集不产出认购率，但仍产出质量类洞察。"""
    generator = InsightGenerator()
    report = generator.generate(sample_test_dataframe, dataset_name="test")

    assert report.positive_rate is None
    assert all(item.category != InsightCategory.BUSINESS for item in report.items)


def test_report_to_dict_serializable(sample_dataframe: pd.DataFrame) -> None:
    """测试：报告可序列化为 JSON 友好的字典结构。"""
    generator = InsightGenerator()
    report = generator.generate(sample_dataframe)
    payload = report.to_dict()

    assert payload["row_count"] == 8
    assert payload["items"][0]["level"] in {"info", "suggest", "warn"}


def test_empty_dataframe_report(sample_dataframe: pd.DataFrame) -> None:
    """测试：空数据报告给出放宽筛选的提示。"""
    generator = InsightGenerator()
    report = generator.generate(sample_dataframe.iloc[0:0])

    assert report.row_count == 0
    assert any("没有样本" in item.title for item in report.items)
