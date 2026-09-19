"""M2 评估指标与业务收益模拟单元测试。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from src.core.model_training.benefit import BusinessBenefitSimulator
from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.evaluation import ModelEvaluator
from src.core.model_training.features import FeatureEngineer
from src.core.model_training.preprocessing import DataPreprocessor


@pytest.fixture
def trained_pipeline(medium_dataframe):
    """供评估测试复用的已训练逻辑回归流水线。"""
    config = ModelTrainingConfig(random_state=42)
    preprocessor = DataPreprocessor(config)
    feature_set = FeatureEngineer(config).transform(medium_dataframe)
    x_train, x_test, y_train, y_test = preprocessor.split(feature_set)
    pipeline = preprocessor.build_pipeline(
        feature_set, LogisticRegression(max_iter=500)
    )
    pipeline.fit(x_train, y_train)
    return pipeline, x_test, y_test


def test_evaluation_metrics_in_valid_range(trained_pipeline):
    """ROC-AUC/PR-AUC 应在 [0,1]，阈值在 (0,1)，混淆矩阵计数一致。"""
    pipeline, x_test, y_test = trained_pipeline
    metrics = ModelEvaluator().evaluate("测试模型", pipeline, x_test, y_test)

    assert 0.5 < metrics.roc_auc <= 1.0
    assert 0.0 < metrics.pr_auc <= 1.0
    assert 0.0 < metrics.threshold < 1.0
    assert metrics.f1 >= 0.0
    tn, fp, fn, tp = (
        metrics.confusion_matrix[0][0],
        metrics.confusion_matrix[0][1],
        metrics.confusion_matrix[1][0],
        metrics.confusion_matrix[1][1],
    )
    assert tn + fp + fn + tp == len(y_test)


def test_benefit_formula_all_call_threshold():
    """阈值为 0（全员外呼）时净收益应等于基线，提升额为 0。"""
    config = ModelTrainingConfig(cost_per_call=10.0, revenue_per_subscription=100.0)
    simulator = BusinessBenefitSimulator(config)
    y_true = pd.Series([1, 0, 1, 0, 0])
    y_proba = pd.Series([0.9, 0.8, 0.7, 0.6, 0.5])

    result = simulator.simulate(y_true, y_proba, threshold=0.0)

    assert result.called_count == 5
    assert result.true_positive_count == 2
    assert result.total_cost == 50.0
    assert result.total_revenue == 200.0
    assert result.net_benefit == 150.0
    assert result.baseline_all_net_benefit == 150.0
    assert result.benefit_lift_vs_all == 0.0


def test_benefit_formula_no_call_threshold():
    """阈值高于所有分数（无人外呼）时收益为 0、成本为 0。"""
    config = ModelTrainingConfig(cost_per_call=10.0, revenue_per_subscription=100.0)
    simulator = BusinessBenefitSimulator(config)
    y_true = pd.Series([1, 0, 1])
    y_proba = pd.Series([0.9, 0.8, 0.7])

    result = simulator.simulate(y_true, y_proba, threshold=0.99)

    assert result.called_count == 0
    assert result.net_benefit == 0.0
    # 基线：3 通电话成本 30，2 个认购收益 200
    assert result.baseline_all_net_benefit == 170.0


def test_threshold_scan_and_best_choice():
    """阈值扫描数量应一致，最优点应选净收益最大者。"""
    simulator = BusinessBenefitSimulator()
    rng = np.random.RandomState(0)
    y_true = pd.Series((rng.rand(200) < 0.3).astype(int))
    # 让正样本分数整体偏高
    y_proba = pd.Series(np.clip(rng.rand(200) + y_true * 0.4, 0, 1))

    results = simulator.simulate_thresholds(y_true, y_proba, (0.3, 0.5, 0.7))
    best = simulator.best_threshold_by_benefit(results)

    assert len(results) == 3
    assert best.net_benefit == max(item.net_benefit for item in results)
