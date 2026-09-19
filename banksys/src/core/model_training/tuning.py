"""超参数调优实现（GridSearchCV，主指标 PR-AUC）。

网格为空时跳过网格搜索直接拟合，供单元测试与快速验证使用。
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.model_selection import GridSearchCV

from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.interfaces import (
    IHyperparameterTuner,
    ModelResult,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GridSearchTuner(IHyperparameterTuner):
    """交叉验证网格调优器。"""

    def __init__(self, config: ModelTrainingConfig | None = None) -> None:
        self.config = config or ModelTrainingConfig()

    def tune(
        self,
        pipeline: Any,
        param_grid: dict,
        x_train: pd.DataFrame,
        y_train: pd.Series,
        model_name: str = "unknown",
    ) -> ModelResult:
        """执行调优并返回结果骨架（指标与收益后续填充）。

        Args:
            pipeline: 含预处理与 model 步骤的 sklearn 流水线。
            param_grid: 超参数网格；为空字典时直接拟合。
            x_train / y_train: 训练特征与 0/1 标签。
            model_name: 模型名称，仅用于日志与结果标识。

        Returns:
            ModelResult：best_params/cv_best_score/metrics 待评估阶段补齐。
        """
        if not param_grid:
            logger.info("[%s] 未提供调优网格，直接拟合（快速模式）", model_name)
            pipeline.fit(x_train, y_train)
            return ModelResult(
                model_name=model_name,
                pipeline=pipeline,
                best_params={},
                cv_best_score=0.0,
            )

        combination_count = 1
        for values in param_grid.values():
            combination_count *= len(values)
        logger.info(
            "[%s] 开始网格搜索：%d 组参数 × %d 折交叉验证",
            model_name,
            combination_count,
            self.config.cv_folds,
        )
        search = GridSearchCV(
            estimator=pipeline,
            param_grid=param_grid,
            scoring=self.config.tuning_scoring,
            cv=self.config.cv_folds,
            n_jobs=-1,
            refit=True,
        )
        search.fit(x_train, y_train)
        logger.success(
            "[%s] 调优完成，最佳 CV %s = %.4f，参数 %s",
            model_name,
            self.config.tuning_scoring,
            search.best_score_,
            search.best_params_,
        )
        return ModelResult(
            model_name=model_name,
            pipeline=search.best_estimator_,
            best_params={
                key.replace("model__", ""): value
                for key, value in search.best_params_.items()
            },
            cv_best_score=float(search.best_score_),
        )
