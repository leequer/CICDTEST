"""模型训练编排：把特征、预处理、调优、评估、收益、落盘串成完整链路。

用法（由 train.py 调用，也可在测试中注入合成数据）：

    orchestrator = TrainingOrchestrator(config)
    report = orchestrator.run()
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import joblib
import pandas as pd

from src.core.data_explorer.loader import CsvDataLoader
from src.core.model_training.benefit import BusinessBenefitSimulator
from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.evaluation import ModelEvaluator
from src.core.model_training.features import FeatureEngineer
from src.core.model_training.interfaces import (
    BenefitResult,
    IBenefitSimulator,
    IFeatureEngineer,
    IHyperparameterTuner,
    IModelEvaluator,
    IModelFactory,
    TrainingReport,
)
from src.core.model_training.models import ModelFactory
from src.core.model_training.preprocessing import DataPreprocessor
from src.core.model_training.tuning import GridSearchTuner
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 业务收益阈值扫描范围（从宽松到严格）
_BENEFIT_THRESHOLDS: tuple[float, ...] = (0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)


class TrainingOrchestrator:
    """模型训练全链路编排器。"""

    def __init__(
        self,
        config: ModelTrainingConfig | None = None,
        *,
        loader: CsvDataLoader | None = None,
        engineer: IFeatureEngineer | None = None,
        preprocessor: DataPreprocessor | None = None,
        factory: IModelFactory | None = None,
        tuner: IHyperparameterTuner | None = None,
        evaluator: IModelEvaluator | None = None,
        simulator: IBenefitSimulator | None = None,
    ) -> None:
        self.config = config or ModelTrainingConfig()
        self.loader = loader or CsvDataLoader(self.config.data_dir)
        self.engineer = engineer or FeatureEngineer(self.config)
        self.preprocessor = preprocessor or DataPreprocessor(self.config)
        self.factory = factory or ModelFactory()
        self.tuner = tuner or GridSearchTuner(self.config)
        self.evaluator = evaluator or ModelEvaluator()
        self.simulator = simulator or BusinessBenefitSimulator(self.config)

    def run(
        self,
        *,
        model_names: tuple[str, ...] | None = None,
        quick: bool = False,
        raw_data: pd.DataFrame | None = None,
    ) -> TrainingReport:
        """执行完整训练流程。

        Args:
            model_names: 参与训练的模型；默认使用配置中的全部四类。
            quick: True 时跳过网格搜索直接拟合（测试/冒烟用）。
            raw_data: 可注入合成数据（测试用）；默认从 data/train.csv 加载。

        Returns:
            TrainingReport：含全部模型结果、最佳模型路径与字段映射路径。
        """
        names = model_names or self.config.model_names
        self.config.ensure_directories()

        logger.info(
            "========== M2 模型训练开始（候选模型：%s，快速模式=%s） ==========",
            names,
            quick,
        )
        raw = raw_data if raw_data is not None else self.loader.load("train")

        # 1. 特征工程 + 字段映射落盘
        feature_set = self.engineer.transform(raw)
        mapping = self.engineer.build_field_mapping(feature_set)
        mapping_path = self.config.db_dir / "field_mapping.json"
        self.engineer.save_field_mapping(mapping, mapping_path)

        # 2. 在原始数据上分层切分（特征工程在流水线首步完成，保证训练/预测同构）
        x_train, x_test, y_train, y_test = self.preprocessor.split_raw(raw)
        scale_pos_weight = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))

        # 3. 逐模型：组装三段式流水线 -> 调优 -> 评估 -> 收益
        results = {}
        for name in names:
            estimator = self.factory.create_estimator(name, scale_pos_weight)
            pipeline = self.preprocessor.build_full_pipeline(feature_set, estimator)
            grid = {} if quick else self.factory.param_grid(name)
            result = self.tuner.tune(pipeline, grid, x_train, y_train, model_name=name)

            metrics = self.evaluator.evaluate(name, result.pipeline, x_test, y_test)
            result.metrics = metrics

            y_proba = pd.Series(result.pipeline.predict_proba(x_test)[:, 1])
            benefit = self.simulator.simulate(y_test, y_proba, metrics.threshold)
            result.benefit = benefit
            results[name] = result

        # 4. 以 PR-AUC 选最佳模型（不平衡场景主指标）
        def _pr_auc(model_name: str) -> float:
            """取某模型测试集 PR-AUC 作为选模型依据。"""
            metrics = results[model_name].metrics
            assert metrics is not None
            return metrics.pr_auc

        best_name = max(results, key=_pr_auc)
        best_pipeline = results[best_name].pipeline
        model_path = self.config.models_dir / "best_model.joblib"
        joblib.dump(best_pipeline, model_path)
        logger.success("最佳模型为 %s，已保存：%s", best_name, model_path)

        # 5. 最佳模型阈值扫描结果与完整报告落盘
        best_proba = pd.Series(best_pipeline.predict_proba(x_test)[:, 1])
        benefit_table = self.simulator.simulate_thresholds(
            y_test, best_proba, _BENEFIT_THRESHOLDS
        )
        report = TrainingReport(
            best_model_name=best_name,
            selection_metric=self.config.tuning_scoring,
            results=results,
            field_mapping_path=mapping_path,
            best_model_path=model_path,
        )
        self._save_report(report, benefit_table)
        logger.success("========== M2 模型训练结束，最佳模型：%s ==========", best_name)
        return report

    def _save_report(
        self, report: TrainingReport, benefit_table: list[BenefitResult]
    ) -> Path:
        """把训练报告与收益阈值表写入 models/training_report.json。"""
        payload = report.summary_dict()
        payload["benefit_threshold_table"] = [item.to_dict() for item in benefit_table]
        payload["business_assumptions"] = {
            "cost_per_call": self.config.cost_per_call,
            "revenue_per_subscription": self.config.revenue_per_subscription,
            "note": "教学占位口径，上线前需业务方按真实财务数据校准",
        }
        report_path = self.config.models_dir / "training_report.json"
        report_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.success("训练报告已保存：%s", report_path)
        return report_path

    def compare_duration_leakage(self, raw: pd.DataFrame | None = None) -> dict:
        """duration 泄露对照实验：同参数逻辑回归，比较纳入/剔除 duration 的指标。

        仅用于量化泄露风险、产出决策证据，不作为正式模型。
        """
        raw = raw if raw is not None else self.loader.load("train")
        comparison: dict[str, dict] = {}

        for include_duration in (False, True):
            config = replace(self.config, include_duration=include_duration)
            engineer = FeatureEngineer(config)
            preprocessor = DataPreprocessor(config)
            feature_set = engineer.transform(raw)
            x_train, x_test, y_train, y_test = preprocessor.split_raw(raw)
            estimator = self.factory.create_estimator("logistic_regression")
            pipeline = preprocessor.build_full_pipeline(feature_set, estimator)
            pipeline.fit(x_train, y_train)
            metrics = self.evaluator.evaluate(
                f"逻辑回归_duration={include_duration}", pipeline, x_test, y_test
            )
            comparison["含duration" if include_duration else "不含duration"] = (
                metrics.to_dict()
            )

        gap = comparison["含duration"]["pr_auc"] - comparison["不含duration"]["pr_auc"]
        comparison["pr_auc差值(含-不含)"] = round(gap, 4)
        logger.warning(
            "duration 对照实验完成，PR-AUC 差值 %.4f：含事后特征的指标虚高即为泄露证据",
            gap,
        )
        if gap < 0:
            logger.info("本次数据中纳入 duration 未带来指标提升，仍应默认隔离")
        return comparison
