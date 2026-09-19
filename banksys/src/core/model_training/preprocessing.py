"""数据切分与 sklearn 预处理实现。

- 目标编码：no=0 / yes=1；
- 数据切分：按目标分层抽样，保证测试集认购率与总体一致；
- 预处理流水线：分类列 OneHot（未知类别忽略，保证上线健壮性），
  数值列标准化；预处理随模型一起序列化为单一 joblib 产物。
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.core.data_explorer import schema
from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.features import FeatureEngineer
from src.core.model_training.interfaces import (
    FeatureSet,
    IDataPreprocessor,
    ModelTrainingError,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RawFeatureTransformer(BaseEstimator, TransformerMixin):
    """原始数据 -> 建模特征宽表的 sklearn 变换器（可随模型一起序列化）。

    保证落盘产物直接接受原始 CSV 行（含 id、不含 subscribe）即可预测，
    特征工程逻辑不会在训练与线上预测之间出现两套实现。
    """

    def __init__(
        self,
        categorical_features: tuple[str, ...],
        numeric_features: tuple[str, ...],
        include_duration: bool = False,
        high_frequency_threshold: int = 6,
        pdays_never_contacted: int = 999,
    ) -> None:
        self.categorical_features = categorical_features
        self.numeric_features = numeric_features
        self.include_duration = include_duration
        self.high_frequency_threshold = high_frequency_threshold
        self.pdays_never_contacted = pdays_never_contacted

    def fit(self, x: pd.DataFrame, y: Any = None) -> "RawFeatureTransformer":
        """特征工程为确定性规则，无需拟合。"""
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        """对原始数据执行特征工程并按固定列顺序输出。"""
        config = ModelTrainingConfig(
            include_duration=self.include_duration,
            high_frequency_threshold=self.high_frequency_threshold,
            pdays_never_contacted=self.pdays_never_contacted,
        )
        feature_set = FeatureEngineer(config).transform(x)
        columns = [*self.categorical_features, *self.numeric_features]
        return feature_set.data[columns].copy()


class DataPreprocessor(IDataPreprocessor):
    """数据切分与 ColumnTransformer 构建器。"""

    def __init__(self, config: ModelTrainingConfig | None = None) -> None:
        self.config = config or ModelTrainingConfig()

    def encode_target(self, target_series: pd.Series) -> pd.Series:
        """yes/no 目标列编码为 1/0。"""
        invalid = set(target_series.unique()) - {
            schema.POSITIVE_LABEL,
            schema.NEGATIVE_LABEL,
        }
        if invalid:
            message = f"目标列出现非 yes/no 取值：{sorted(invalid)}"
            logger.error(message)
            raise ModelTrainingError(message)
        return (target_series == schema.POSITIVE_LABEL).astype(int)

    def split(
        self, feature_set: FeatureSet
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """分层切分训练/测试集。

        Returns:
            x_train, x_test, y_train, y_test
        """
        data = feature_set.data
        if feature_set.target not in data.columns:
            message = "特征宽表缺少目标列 subscribe，无法切分（测试集不能用于监督训练）"
            logger.error(message)
            raise ModelTrainingError(message)

        features = data.drop(columns=[feature_set.target])
        target = self.encode_target(data[feature_set.target])
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=target,
        )
        logger.info(
            "分层切分完成：训练 %d 行 认购率 %.2f%%；测试 %d 行 认购率 %.2f%%",
            len(x_train),
            y_train.mean() * 100,
            len(x_test),
            y_test.mean() * 100,
        )
        return x_train, x_test, y_train, y_test

    def build_column_transformer(self, feature_set: FeatureSet) -> ColumnTransformer:
        """构建分类 OneHot + 数值标准化的列变换器。"""
        categorical = list(feature_set.categorical_features)
        numeric = list(feature_set.numeric_features)

        transformers = []
        if categorical:
            transformers.append(
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    categorical,
                )
            )
        if numeric:
            transformers.append(("numeric", StandardScaler(), numeric))

        return ColumnTransformer(
            transformers=transformers,
            remainder="drop",
            verbose_feature_names_out=False,
        )

    def split_raw(
        self, raw: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """在原始数据（含目标列）上分层切分，X 保留原始列，由流水线首步处理。"""
        if schema.TARGET_COLUMN not in raw.columns:
            message = "原始数据缺少目标列 subscribe，无法切分"
            logger.error(message)
            raise ModelTrainingError(message)

        features = raw.drop(columns=[schema.TARGET_COLUMN])
        target = self.encode_target(raw[schema.TARGET_COLUMN])
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=target,
        )
        logger.info(
            "分层切分完成：训练 %d 行 认购率 %.2f%%；测试 %d 行 认购率 %.2f%%",
            len(x_train),
            y_train.mean() * 100,
            len(x_test),
            y_test.mean() * 100,
        )
        return x_train, x_test, y_train, y_test

    def build_pipeline(self, feature_set: FeatureSet, estimator: Any) -> Pipeline:
        """把预处理与估计器组装为单一 sklearn 流水线（输入为已完成特征工程的宽表）。"""
        return Pipeline(
            steps=[
                ("preprocess", self.build_column_transformer(feature_set)),
                ("model", estimator),
            ]
        )

    def build_full_pipeline(self, feature_set: FeatureSet, estimator: Any) -> Pipeline:
        """组装三段式流水线：原始特征工程 -> 列预处理 -> 模型。

        落盘后可直接对原始 CSV（无标签）调用 predict_proba。
        """
        raw_transformer = RawFeatureTransformer(
            categorical_features=feature_set.categorical_features,
            numeric_features=feature_set.numeric_features,
            include_duration=self.config.include_duration,
            high_frequency_threshold=self.config.high_frequency_threshold,
            pdays_never_contacted=self.config.pdays_never_contacted,
        )
        return Pipeline(
            steps=[
                ("features", raw_transformer),
                ("preprocess", self.build_column_transformer(feature_set)),
                ("model", estimator),
            ]
        )
