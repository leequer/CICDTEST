"""模型评估实现。

金融营销场景正负样本约 87:13，单纯准确率没有业务意义，
因此以 ROC-AUC 与 PR-AUC（平均精度）为核心指标，
并在精确率-召回率曲线上搜索 F1 最优决策阈值，
供业务在“外呼成本”与“认购捕获率”之间取舍。
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    precision_recall_fscore_support,
    roc_auc_score,
)

from src.core.model_training.interfaces import (
    EvaluationMetrics,
    IModelEvaluator,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModelEvaluator(IModelEvaluator):
    """在独立测试集上评估已训练流水线。"""

    def evaluate(
        self,
        model_name: str,
        pipeline: Any,
        x_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> EvaluationMetrics:
        """计算全量指标并选取 F1 最优阈值。"""
        y_proba = pipeline.predict_proba(x_test)[:, 1]

        roc_auc = float(roc_auc_score(y_test, y_proba))
        pr_auc = float(average_precision_score(y_test, y_proba))

        precision_curve, recall_curve, threshold_curve = precision_recall_curve(
            y_test, y_proba
        )
        best_threshold, best_f1 = self._find_best_f1_threshold(
            precision_curve, recall_curve, threshold_curve
        )

        y_pred = (y_proba >= best_threshold).astype(int)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test,
            y_pred,
            average="binary",
            zero_division=0,
        )
        accuracy = float(accuracy_score(y_test, y_pred))
        matrix = confusion_matrix(y_test, y_pred, labels=(0, 1)).tolist()

        metrics = EvaluationMetrics(
            model_name=model_name,
            roc_auc=roc_auc,
            pr_auc=pr_auc,
            threshold=float(best_threshold),
            precision=float(precision),
            recall=float(recall),
            f1=float(f1),
            accuracy=accuracy,
            confusion_matrix=matrix,
            precision_curve=[float(v) for v in precision_curve],
            recall_curve=[float(v) for v in recall_curve],
            threshold_curve=[float(v) for v in threshold_curve],
        )
        logger.success(
            "[%s] 测试集 ROC-AUC=%.4f PR-AUC=%.4f 最优阈值=%.3f "
            "精确率=%.4f 召回率=%.4f F1=%.4f",
            model_name,
            roc_auc,
            pr_auc,
            best_threshold,
            precision,
            recall,
            f1,
        )
        return metrics

    @staticmethod
    def _find_best_f1_threshold(
        precision_curve: np.ndarray,
        recall_curve: np.ndarray,
        threshold_curve: np.ndarray,
    ) -> tuple[float, float]:
        """在 PR 曲线上搜索 F1 最大的阈值。

        precision_recall_curve 返回的 precision/recall 比 threshold 多一个点，
        最后一个点对应阈值 1.0（精度=1、召回=0），不参与搜索。
        """
        precisions = precision_curve[:-1]
        recalls = recall_curve[:-1]
        denominator = precisions + recalls
        f1_scores = np.divide(
            2 * precisions * recalls,
            denominator,
            out=np.zeros_like(precisions),
            where=denominator > 0,
        )
        best_index = int(np.argmax(f1_scores))
        return float(threshold_curve[best_index]), float(f1_scores[best_index])
