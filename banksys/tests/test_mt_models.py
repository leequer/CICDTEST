"""M2 模型工厂与四类模型可训练性测试。"""

from __future__ import annotations

import pytest

from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.features import FeatureEngineer
from src.core.model_training.interfaces import ModelTrainingError
from src.core.model_training.models import ModelFactory
from src.core.model_training.preprocessing import DataPreprocessor


def test_factory_creates_all_four_models():
    """工厂应能创建四类候选模型。"""
    factory = ModelFactory()
    for name in ModelFactory.SUPPORTED_MODELS:
        estimator = factory.create_estimator(name, scale_pos_weight=6.0)
        assert estimator is not None
        grid = factory.param_grid(name)
        assert all(key.startswith("model__") for key in grid)
        assert grid


def test_factory_rejects_unknown_model():
    """未知模型名应抛出中文异常。"""
    with pytest.raises(ModelTrainingError):
        ModelFactory().create_estimator("deep_learning")


@pytest.mark.parametrize("model_name", ModelFactory.SUPPORTED_MODELS)
def test_each_model_trains_and_predicts_probability(model_name, medium_dataframe):
    """四类模型走完整流水线后应输出合法正类概率。

    使用快速配置直接拟合（不做网格搜索），保证测试速度。
    """
    config = ModelTrainingConfig(random_state=42)
    preprocessor = DataPreprocessor(config)
    feature_set = FeatureEngineer(config).transform(medium_dataframe)
    x_train, x_test, y_train, _ = preprocessor.split(feature_set)

    estimator = ModelFactory().create_estimator(model_name, scale_pos_weight=4.0)
    pipeline = preprocessor.build_pipeline(feature_set, estimator)
    pipeline.fit(x_train, y_train)

    probabilities = pipeline.predict_proba(x_test.head(10))[:, 1]
    assert probabilities.shape == (10,)
    assert ((probabilities >= 0.0) & (probabilities <= 1.0)).all()
