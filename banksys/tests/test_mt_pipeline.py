"""M2 训练编排端到端测试（合成数据 + 快速模式 + 临时目录）。"""

from __future__ import annotations

import json

import joblib

from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.pipeline import TrainingOrchestrator


def test_run_quick_produces_all_artifacts(medium_dataframe, tmp_path):
    """快速模式应产出：字段映射、最佳模型 joblib、训练报告 JSON。"""
    config = ModelTrainingConfig(random_state=42, project_root=tmp_path)
    orchestrator = TrainingOrchestrator(config)

    report = orchestrator.run(
        model_names=("logistic_regression",),
        quick=True,
        raw_data=medium_dataframe,
    )

    assert report.best_model_name == "logistic_regression"
    assert config.db_dir.joinpath("field_mapping.json").exists()
    assert config.models_dir.joinpath("best_model.joblib").exists()

    # 落盘产物必须能直接吃“原始无标签行”（M3 在线预测契约）
    artifact = joblib.load(config.models_dir / "best_model.joblib")
    raw_unlabeled = medium_dataframe.drop(columns=["subscribe"]).head(5)
    probabilities = artifact.predict_proba(raw_unlabeled)[:, 1]
    assert probabilities.shape == (5,)
    assert [name for name, _ in artifact.steps] == ["features", "preprocess", "model"]

    report_path = config.models_dir / "training_report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["best_model_name"] == "logistic_regression"
    metrics = payload["models"]["logistic_regression"]["metrics"]
    assert 0.0 <= metrics["roc_auc"] <= 1.0
    assert payload["benefit_threshold_table"]
    assert payload["business_assumptions"]["note"]


def test_compare_duration_leakage_returns_both_views(medium_dataframe, tmp_path):
    """duration 对照实验应同时返回含/不含两组指标。"""
    config = ModelTrainingConfig(random_state=42, project_root=tmp_path)
    orchestrator = TrainingOrchestrator(config)

    comparison = orchestrator.compare_duration_leakage(raw=medium_dataframe)

    assert "不含duration" in comparison
    assert "含duration" in comparison
    assert "pr_auc差值(含-不含)" in comparison
