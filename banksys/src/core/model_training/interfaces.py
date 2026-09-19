"""模型训练模块接口定义（接口先行原则）。

仅包含抽象基类、数据契约与异常定义，供 features / preprocessing /
models / tuning / evaluation / benefit / pipeline 共同遵守。

接口契约总览：
- IFeatureEngineer    ：原始数据 -> 建模宽表，产出字段映射
- IDataPreprocessor   ：切分数据、构建 sklearn 预处理流水线
- IModelFactory       ：按名称创建估计器与超参数网格
- IHyperparameterTuner：交叉验证调优
- IModelEvaluator     ：金融场景指标评估
- IBenefitSimulator   ：营销成本收益业务模拟
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


class ModelTrainingError(Exception):
    """模型训练模块统一异常基类（消息必须为面向用户的简体中文）。"""


@dataclass(frozen=True)
class FeatureSet:
    """建模特征集合契约。

    Attributes:
        data: 完成特征工程后的宽表（含目标列）。
        categorical_features: 参与 OneHot 编码的分类特征名。
        numeric_features: 参与标准化的数值特征名。
        target: 目标列名。
    """

    data: pd.DataFrame
    categorical_features: tuple[str, ...]
    numeric_features: tuple[str, ...]
    target: str


@dataclass
class EvaluationMetrics:
    """分类评估指标契约（金融营销不平衡场景）。

    Attributes:
        model_name: 模型名称。
        roc_auc: ROC 曲线下面积。
        pr_auc: 精确率-召回率曲线下面积（平均精度，主选模型指标）。
        threshold: 实际采用的决策阈值。
        precision / recall / f1 / accuracy: 该阈值下的混淆矩阵指标。
        confusion_matrix: [[真负, 假正], [假负, 真正]]。
        precision_curve / recall_curve / threshold_curve: PR 曲线数据，供增益分析。
    """

    model_name: str
    roc_auc: float
    pr_auc: float
    threshold: float
    precision: float
    recall: float
    f1: float
    accuracy: float
    confusion_matrix: list[list[int]]
    precision_curve: list[float] = field(default_factory=list)
    recall_curve: list[float] = field(default_factory=list)
    threshold_curve: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转为可 JSON 序列化字典（曲线数据不纳入，避免报告过大）。"""
        return {
            "model_name": self.model_name,
            "roc_auc": round(self.roc_auc, 4),
            "pr_auc": round(self.pr_auc, 4),
            "threshold": round(self.threshold, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "accuracy": round(self.accuracy, 4),
            "confusion_matrix": self.confusion_matrix,
        }


@dataclass(frozen=True)
class BenefitResult:
    """单阈值下的业务收益模拟结果。

    Attributes:
        threshold: 决策阈值（分数 >= 阈值则外呼）。
        called_count: 计划外呼客户数。
        call_rate: 外呼覆盖率。
        true_positive_count: 外呼命中的认购客户数。
        precision: 外呼名单认购率（投入有效性）。
        recall: 认购客户捕获率（机会覆盖率）。
        total_cost: 外呼总成本。
        total_revenue: 命中客户总收益。
        net_benefit: 净收益（总收益 - 总成本）。
        baseline_all_net_benefit: “全员外呼”基线净收益。
        benefit_lift_vs_all: 相对全员外呼的净收益提升额。
    """

    threshold: float
    called_count: int
    call_rate: float
    true_positive_count: int
    precision: float
    recall: float
    total_cost: float
    total_revenue: float
    net_benefit: float
    baseline_all_net_benefit: float
    benefit_lift_vs_all: float

    def to_dict(self) -> dict:
        """转为可 JSON 序列化字典。"""
        return {
            "threshold": round(self.threshold, 4),
            "called_count": self.called_count,
            "call_rate": round(self.call_rate, 4),
            "true_positive_count": self.true_positive_count,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "total_cost": round(self.total_cost, 2),
            "total_revenue": round(self.total_revenue, 2),
            "net_benefit": round(self.net_benefit, 2),
            "baseline_all_net_benefit": round(self.baseline_all_net_benefit, 2),
            "benefit_lift_vs_all": round(self.benefit_lift_vs_all, 2),
        }


@dataclass
class ModelResult:
    """单个模型的训练-调优-评估结果。

    Attributes:
        model_name: 模型名称。
        pipeline: 含预处理步骤的完整 sklearn 流水线。
        best_params: 调优得到的最佳超参数。
        cv_best_score: 交叉验证最佳分数（PR-AUC）。
        metrics: 测试集评估指标。
        benefit: 推荐阈值下的业务收益结果。
    """

    model_name: str
    pipeline: Any
    best_params: dict
    cv_best_score: float
    metrics: EvaluationMetrics | None = None
    benefit: BenefitResult | None = None


@dataclass
class TrainingReport:
    """全量训练报告契约。"""

    best_model_name: str
    selection_metric: str
    results: dict[str, ModelResult]
    field_mapping_path: Path
    best_model_path: Path

    def summary_dict(self) -> dict:
        """生成可写入 JSON 的摘要（不含不可序列化的流水线对象）。"""
        models_summary: dict[str, dict] = {}
        for name, result in self.results.items():
            # 训练编排结束后指标与收益必然已填充
            assert result.metrics is not None
            assert result.benefit is not None
            models_summary[name] = {
                "cv_best_score": round(result.cv_best_score, 4),
                "best_params": result.best_params,
                "metrics": result.metrics.to_dict(),
                "benefit": result.benefit.to_dict(),
            }
        return {
            "best_model_name": self.best_model_name,
            "selection_metric": self.selection_metric,
            "field_mapping_path": str(self.field_mapping_path),
            "best_model_path": str(self.best_model_path),
            "models": models_summary,
        }


class IFeatureEngineer(ABC):
    """特征工程接口。"""

    @abstractmethod
    def transform(self, raw: pd.DataFrame) -> FeatureSet:
        """原始数据 -> 建模宽表与特征清单。"""
        raise NotImplementedError

    @abstractmethod
    def build_field_mapping(self, feature_set: FeatureSet) -> dict:
        """生成字段映射表结构（原始字段 -> 衍生特征 -> 编码方式）。"""
        raise NotImplementedError

    @abstractmethod
    def save_field_mapping(self, mapping: dict, path: Path) -> None:
        """把字段映射表以 UTF-8 JSON 落盘到 db/field_mapping.json。"""
        raise NotImplementedError


class IDataPreprocessor(ABC):
    """数据切分与预处理接口。"""

    @abstractmethod
    def encode_target(self, target_series: pd.Series) -> pd.Series:
        """yes/no 目标列编码为 1/0。"""
        raise NotImplementedError

    @abstractmethod
    def split(
        self, feature_set: FeatureSet
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """分层切分训练集/测试集，返回 X_train, X_test, y_train, y_test。"""
        raise NotImplementedError

    @abstractmethod
    def build_column_transformer(self, feature_set: FeatureSet) -> object:
        """构建 ColumnTransformer（分类 OneHot + 数值标准化）。"""
        raise NotImplementedError


class IModelFactory(ABC):
    """模型工厂接口。"""

    @abstractmethod
    def create_estimator(self, model_name: str, scale_pos_weight: float = 1.0) -> Any:
        """按名称创建未训练的估计器。"""
        raise NotImplementedError

    @abstractmethod
    def param_grid(self, model_name: str) -> dict:
        """返回该模型的调优网格（键为流水线参数路径 model__xxx）。"""
        raise NotImplementedError


class IHyperparameterTuner(ABC):
    """超参数调优接口。"""

    @abstractmethod
    def tune(
        self,
        pipeline: Any,
        param_grid: dict,
        x_train: pd.DataFrame,
        y_train: pd.Series,
        model_name: str = "unknown",
    ) -> ModelResult:
        """交叉验证调优，返回带最佳流水线的结果骨架。

        网格为空时直接拟合，不做网格搜索（供快速测试使用）。
        """
        raise NotImplementedError


class IModelEvaluator(ABC):
    """模型评估接口。"""

    @abstractmethod
    def evaluate(
        self, model_name: str, pipeline: Any, x_test: pd.DataFrame, y_test: pd.Series
    ) -> EvaluationMetrics:
        """在测试集计算 ROC-AUC、PR-AUC、F1 等指标，并选取 F1 最优阈值。"""
        raise NotImplementedError


class IBenefitSimulator(ABC):
    """业务收益模拟接口。"""

    @abstractmethod
    def simulate(
        self,
        y_true: pd.Series,
        y_proba: pd.Series,
        threshold: float,
    ) -> BenefitResult:
        """按给定阈值模拟外呼名单的成本与收益。"""
        raise NotImplementedError

    @abstractmethod
    def simulate_thresholds(
        self,
        y_true: pd.Series,
        y_proba: pd.Series,
        thresholds: tuple[float, ...],
    ) -> list[BenefitResult]:
        """批量模拟多个阈值，供选择业务最优外呼比例。"""
        raise NotImplementedError
