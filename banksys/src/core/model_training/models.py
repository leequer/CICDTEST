"""模型工厂：统一创建四类候选模型与调优网格。

候选模型：
- logistic_regression：逻辑回归基线（线性、可解释、依赖标准化）；
- random_forest：随机森林（非线性、抗异常值）；
- xgboost：梯度提升树（工业界常用强基线）；
- lightgbm：轻量梯度提升树（训练快、类别关系建模强）。

类别不平衡通过类权重 / scale_pos_weight 处理；
网格保持精简，保证 CPU 环境下训练时长可控。
"""

from __future__ import annotations

from typing import Any

from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from src.core.model_training.interfaces import IModelFactory, ModelTrainingError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModelFactory(IModelFactory):
    """创建估计器与超参数网格的统一工厂。"""

    #: 支持的模型名称
    SUPPORTED_MODELS: tuple[str, ...] = (
        "logistic_regression",
        "random_forest",
        "xgboost",
        "lightgbm",
    )

    def create_estimator(self, model_name: str, scale_pos_weight: float = 1.0) -> Any:
        """按名称创建未训练估计器。

        Args:
            model_name: 模型名称（见 SUPPORTED_MODELS）。
            scale_pos_weight: 正样本权重（负样本数/正样本数），供提升树使用。

        Raises:
            ModelTrainingError: 不支持的模型名称。
        """
        if model_name == "logistic_regression":
            return LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42,
            )
        if model_name == "random_forest":
            return RandomForestClassifier(
                n_estimators=200,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=42,
            )
        if model_name == "xgboost":
            return XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.9,
                colsample_bytree=0.9,
                tree_method="hist",
                eval_metric="aucpr",
                n_jobs=-1,
                random_state=42,
                scale_pos_weight=scale_pos_weight,
            )
        if model_name == "lightgbm":
            return LGBMClassifier(
                n_estimators=300,
                num_leaves=31,
                learning_rate=0.1,
                subsample=0.9,
                colsample_bytree=0.9,
                n_jobs=-1,
                random_state=42,
                is_unbalance=True,
                verbosity=-1,
            )

        message = f"不支持的模型名称：{model_name}，可选 {self.SUPPORTED_MODELS}"
        logger.error(message)
        raise ModelTrainingError(message)

    def param_grid(self, model_name: str) -> dict:
        """返回精简调优网格（键前缀 model__ 对应流水线中的步骤名）。

        Raises:
            ModelTrainingError: 不支持的模型名称。
        """
        grids: dict[str, dict] = {
            "logistic_regression": {
                "model__C": (0.1, 1.0, 10.0),
            },
            "random_forest": {
                "model__n_estimators": (200,),
                "model__max_depth": (6, 12, None),
                "model__min_samples_leaf": (1, 5),
            },
            "xgboost": {
                "model__n_estimators": (200,),
                "model__max_depth": (4, 6),
                "model__learning_rate": (0.05, 0.1),
            },
            "lightgbm": {
                "model__n_estimators": (300,),
                "model__num_leaves": (31, 63),
                "model__learning_rate": (0.05, 0.1),
            },
        }
        if model_name not in grids:
            message = f"不支持的模型名称：{model_name}，可选 {tuple(grids.keys())}"
            logger.error(message)
            raise ModelTrainingError(message)
        return grids[model_name]
