"""模型训练模块（M2）。

提供从原始 CSV 到可部署模型的完整链路：
特征工程 -> 数据切分与预处理 -> 多模型训练与调优 -> 金融指标评估 -> 业务收益模拟。

所有模块不依赖 Streamlit，可独立运行与单元测试。
"""

from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.features import FeatureEngineer
from src.core.model_training.preprocessing import DataPreprocessor

__all__ = [
    "ModelTrainingConfig",
    "FeatureEngineer",
    "DataPreprocessor",
]
