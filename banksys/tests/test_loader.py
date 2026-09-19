"""数据加载器单元测试。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.core.data_explorer import schema
from src.core.data_explorer.loader import CsvDataLoader, DataLoadingError


def test_load_train_csv_success(data_dir_with_csvs: Path) -> None:
    """测试：正常加载训练集并完成类型校正。"""
    loader = CsvDataLoader(data_dir=data_dir_with_csvs)
    data = loader.load("train")

    assert list(data.columns) == list(schema.ALL_COLUMNS)
    assert len(data) == 8
    assert data[schema.TARGET_COLUMN].isin(["yes", "no"]).all()
    assert pd.api.types.is_numeric_dtype(data["age"])


def test_load_test_csv_without_target(data_dir_with_csvs: Path) -> None:
    """测试：测试集无目标列时正常加载。"""
    loader = CsvDataLoader(data_dir=data_dir_with_csvs)
    data = loader.load("test")

    assert schema.TARGET_COLUMN not in data.columns
    assert list(data.columns) == list(schema.TEST_COLUMNS)


def test_describe_train_meta(data_dir_with_csvs: Path) -> None:
    """测试：训练集元信息（行数、认购率）正确。"""
    loader = CsvDataLoader(data_dir=data_dir_with_csvs)
    meta = loader.describe("train")

    assert meta.name == "train"
    assert meta.row_count == 8
    assert meta.has_target is True
    assert meta.positive_count == 3
    assert meta.negative_count == 5
    assert meta.positive_rate == 0.375


def test_load_missing_file_raises(tmp_path: Path) -> None:
    """测试：文件不存在时抛出中文业务异常。"""
    loader = CsvDataLoader(data_dir=tmp_path)
    with pytest.raises(DataLoadingError, match="数据文件不存在"):
        loader.load("train")


def test_load_missing_column_raises(
    tmp_path: Path, sample_dataframe: pd.DataFrame
) -> None:
    """测试：缺少必需字段时抛出异常并指明字段名。"""
    broken = sample_dataframe.drop(columns=["age"])
    broken.to_csv(tmp_path / "train.csv", index=False)
    loader = CsvDataLoader(data_dir=tmp_path)

    with pytest.raises(DataLoadingError, match="缺失必需字段"):
        loader.load("train")


def test_unknown_dataset_name_raises(data_dir_with_csvs: Path) -> None:
    """测试：非法数据集名称被拒绝。"""
    loader = CsvDataLoader(data_dir=data_dir_with_csvs)
    with pytest.raises(DataLoadingError, match="不支持的数据集名称"):
        loader.load("validation")
