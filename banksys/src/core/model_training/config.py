"""模型训练配置（全链路唯一参数事实来源）。

业务参数（单次外呼成本、单笔认购收益）为教学场景占位值，
上线前必须由业务方按真实财务口径校准（见 PRD 第 10 章风险）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.utils.logger import get_project_root


@dataclass(frozen=True)
class ModelTrainingConfig:
    """模型训练配置。

    Attributes:
        random_state: 全局随机种子，保证训练可复现。
        test_size: 测试集比例（分层抽样）。
        include_duration: 是否纳入 duration 特征。默认 False——
            duration 是通话结束后才可知的事后特征，纳入即数据泄露（DEC-008）。
        high_frequency_threshold: 高频触达阈值，campaign 达到该值判定为过度触达。
        pdays_never_contacted: pdays 哨兵值，表示此前从未联系。
        cv_folds: 网格搜索交叉验证折数。
        tuning_scoring: 调优主指标；不平衡场景采用平均精度（PR-AUC）。
        cost_per_call: 单次电话外呼成本（元，占位值，待业务校准）。
        revenue_per_subscription: 成功认购一笔带来的收益（元，占位值，待业务校准）。
        model_names: 本次参与训练与比较的模型名称。
        data_dir / models_dir / db_dir: 数据、模型、字段映射产物目录。
    """

    random_state: int = 42
    test_size: float = 0.2
    include_duration: bool = False
    high_frequency_threshold: int = 6
    pdays_never_contacted: int = 999
    cv_folds: int = 3
    tuning_scoring: str = "average_precision"

    # 业务收益模拟参数（占位值，需业务方校准）
    cost_per_call: float = 10.0
    revenue_per_subscription: float = 100.0

    model_names: tuple[str, ...] = (
        "logistic_regression",
        "random_forest",
        "xgboost",
        "lightgbm",
    )

    project_root: Path = field(default_factory=get_project_root)

    @property
    def data_dir(self) -> Path:
        """原始数据目录。"""
        return self.project_root / "data"

    @property
    def models_dir(self) -> Path:
        """模型产物目录（joblib，默认不提交 git）。"""
        return self.project_root / "models"

    @property
    def db_dir(self) -> Path:
        """字段映射等结构化元数据目录。"""
        return self.project_root / "db"

    def ensure_directories(self) -> None:
        """创建产物目录（幂等）。"""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.db_dir.mkdir(parents=True, exist_ok=True)
