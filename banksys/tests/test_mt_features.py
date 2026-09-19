"""M2 特征工程单元测试。"""

from __future__ import annotations

import json

from src.core.data_explorer import schema
from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.features import FeatureEngineer
from src.core.model_training.interfaces import ModelTrainingError


def test_transform_drops_identifier_and_duration(sample_dataframe):
    """默认配置下应剔除 id 与泄露特征 duration。"""
    feature_set = FeatureEngineer().transform(sample_dataframe)

    assert schema.ID_COLUMN not in feature_set.data.columns
    assert "duration" not in feature_set.data.columns
    assert schema.TARGET_COLUMN in feature_set.data.columns
    assert "age_bucket" in feature_set.categorical_features


def test_derived_features_values(sample_dataframe):
    """衍生特征取值应符合业务规则。"""
    feature_set = FeatureEngineer().transform(sample_dataframe)
    data = feature_set.data

    row_never_contacted = sample_dataframe["pdays"] == 999
    assert (data.loc[row_never_contacted.values, "is_ever_contacted"] == 0).all()
    assert (data.loc[~row_never_contacted.values, "is_ever_contacted"] == 1).all()

    row_high_frequency = sample_dataframe["campaign"] >= 6
    assert (data.loc[row_high_frequency.values, "is_high_frequency"] == 1).all()

    row_success = sample_dataframe["poutcome"] == "success"
    assert (data.loc[row_success.values, "was_previous_success"] == 1).all()

    row_cellular = sample_dataframe["contact"] == "cellular"
    assert (data.loc[row_cellular.values, "contact_cellular"] == 1).all()


def test_include_duration_keeps_leakage_feature(sample_dataframe):
    """显式开启 include_duration 时应保留 duration（仅用于对照实验）。"""
    config = ModelTrainingConfig(include_duration=True)
    feature_set = FeatureEngineer(config).transform(sample_dataframe)

    assert "duration" in feature_set.data.columns
    assert "duration" in feature_set.numeric_features


def test_missing_required_column_raises(sample_dataframe):
    """缺少必需字段时应抛出中文业务异常。"""
    broken = sample_dataframe.drop(columns=["age"])
    try:
        FeatureEngineer().transform(broken)
    except ModelTrainingError as exc:
        assert "缺少必需字段" in str(exc)
    else:  # pragma: no cover - 未抛异常即失败
        raise AssertionError("缺少必需字段时未抛出 ModelTrainingError")


def test_field_mapping_saved_as_utf8_json(sample_dataframe, tmp_path):
    """字段映射表应包含全部约定段落并可被 JSON 读回。"""
    engineer = FeatureEngineer()
    feature_set = engineer.transform(sample_dataframe)
    mapping = engineer.build_field_mapping(feature_set)

    assert set(mapping["衍生特征"]) == {
        "is_ever_contacted",
        "is_high_frequency",
        "was_previous_success",
        "contact_cellular",
        "age_bucket",
    }
    assert mapping["目标字段"]["编码"] == {"no": 0, "yes": 1}
    assert "duration" in mapping["剔除字段"]

    target = tmp_path / "field_mapping.json"
    engineer.save_field_mapping(mapping, target)
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["建模特征清单"]["numeric"]
    assert loaded["建模特征清单"]["categorical"]
