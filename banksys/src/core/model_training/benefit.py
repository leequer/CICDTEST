"""业务收益模拟实现。

模拟规则（教学占位口径，上线前由业务方按真实财务数据校准）：
- 对预测分数 >= 阈值的客户发起外呼，每通电话成本 cost_per_call 元；
- 外呼命中真实认购客户，获得 revenue_per_subscription 元收益；
- 未命中只损失外呼成本；不外呼则既无成本也无收益。

输出还给出“全员外呼”基线的净收益，便于量化精准营销省了多少钱。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.interfaces import (
    BenefitResult,
    IBenefitSimulator,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BusinessBenefitSimulator(IBenefitSimulator):
    """基于混淆矩阵计数的营销收益模拟器。"""

    def __init__(self, config: ModelTrainingConfig | None = None) -> None:
        self.config = config or ModelTrainingConfig()

    def simulate(
        self,
        y_true: pd.Series,
        y_proba: pd.Series,
        threshold: float,
    ) -> BenefitResult:
        """计算单个阈值下的外呼成本、收益与基线对比。"""
        true_labels = np.asarray(y_true, dtype=int)
        probabilities = np.asarray(y_proba, dtype=float)
        predictions = (probabilities >= threshold).astype(int)

        total_count = len(true_labels)
        total_positive = int(true_labels.sum())
        called_count = int(predictions.sum())
        true_positive = int(((predictions == 1) & (true_labels == 1)).sum())

        total_cost = called_count * self.config.cost_per_call
        total_revenue = true_positive * self.config.revenue_per_subscription
        net_benefit = total_revenue - total_cost

        # 全员外呼基线：所有客户都打，所有认购客户都能转化
        baseline_cost = total_count * self.config.cost_per_call
        baseline_revenue = total_positive * self.config.revenue_per_subscription
        baseline_net = baseline_revenue - baseline_cost

        result = BenefitResult(
            threshold=threshold,
            called_count=called_count,
            call_rate=called_count / total_count if total_count else 0.0,
            true_positive_count=true_positive,
            precision=true_positive / called_count if called_count else 0.0,
            recall=true_positive / total_positive if total_positive else 0.0,
            total_cost=total_cost,
            total_revenue=total_revenue,
            net_benefit=net_benefit,
            baseline_all_net_benefit=baseline_net,
            benefit_lift_vs_all=net_benefit - baseline_net,
        )
        logger.info(
            "阈值 %.2f：外呼 %d/%d 人（%.1f%%），命中 %d，净收益 %.0f 元，"
            "较全员外呼提升 %.0f 元",
            threshold,
            called_count,
            total_count,
            result.call_rate * 100,
            true_positive,
            net_benefit,
            result.benefit_lift_vs_all,
        )
        return result

    def simulate_thresholds(
        self,
        y_true: pd.Series,
        y_proba: pd.Series,
        thresholds: tuple[float, ...],
    ) -> list[BenefitResult]:
        """批量模拟多个阈值。"""
        return [self.simulate(y_true, y_proba, threshold) for threshold in thresholds]

    def best_threshold_by_benefit(self, results: list[BenefitResult]) -> BenefitResult:
        """从模拟结果中挑选净收益最高的阈值方案。"""
        return max(results, key=lambda result: result.net_benefit)
