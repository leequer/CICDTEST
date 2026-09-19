"""M2 数据切分与预处理单元测试。"""

from __future__ import annotations

from sklearn.linear_model import LogisticRegression

from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.features import FeatureEngineer
from src.core.model_training.interfaces import ModelTrainingError
from src.core.model_training.preprocessing import (
    DataPreprocessor,
    RawFeatureTransformer,
)


def test_encode_target(sample_dataframe):
    """yes/no 应编码为 1/0。"""
    preprocessor = DataPreprocessor()
    encoded = preprocessor.encode_target(sample_dataframe["subscribe"])

    assert set(encoded.unique()) == {0, 1}
    assert (encoded[sample_dataframe["subscribe"] == "yes"] == 1).all()


def test_encode_target_rejects_invalid_label(sample_dataframe):
    """非 yes/no 取值应抛出中文异常。"""
    invalid = sample_dataframe["subscribe"].copy()
    invalid.iloc[0] = "maybe"
    try:
        DataPreprocessor().encode_target(invalid)
    except ModelTrainingError as exc:
        assert "非 yes/no" in str(exc)
    else:  # pragma: no cover - 未抛异常即失败
        raise AssertionError("非法目标值未抛出异常")


def test_stratified_split_shape_and_rate(medium_dataframe):
    """切分比例应符合配置，训练/测试认购率应接近（分层抽样）。"""
    config = ModelTrainingConfig(test_size=0.25)
    feature_set = FeatureEngineer(config).transform(medium_dataframe)
    x_train, x_test, y_train, y_test = DataPreprocessor(config).split(feature_set)

    assert len(x_train) + len(x_test) == len(medium_dataframe)
    assert abs(len(x_test) / len(medium_dataframe) - 0.25) < 0.02
    assert abs(y_train.mean() - y_test.mean()) < 0.12
    assert "subscribe" not in x_train.columns


def test_raw_transformer_outputs_only_model_columns(medium_dataframe):
    """原始变换器应剔除 id/目标列与 duration，仅输出建模特征列。"""
    config = ModelTrainingConfig()
    feature_set = FeatureEngineer(config).transform(medium_dataframe)
    transformer = RawFeatureTransformer(
        categorical_features=feature_set.categorical_features,
        numeric_features=feature_set.numeric_features,
    )

    engineered = transformer.fit_transform(medium_dataframe)

    assert "id" not in engineered.columns
    assert "subscribe" not in engineered.columns
    assert "duration" not in engineered.columns
    assert "is_ever_contacted" in engineered.columns
    assert list(engineered.columns) == [
        *feature_set.categorical_features,
        *feature_set.numeric_features,
    ]


def test_full_pipeline_predicts_raw_unlabeled_rows(medium_dataframe):
    """三段式流水线必须能直接对“无标签原始行”输出概率（上线契约）。"""
    config = ModelTrainingConfig(random_state=42)
    preprocessor = DataPreprocessor(config)
    feature_set = FeatureEngineer(config).transform(medium_dataframe)
    x_train, _, y_train, _ = preprocessor.split_raw(medium_dataframe)

    pipeline = preprocessor.build_full_pipeline(
        feature_set, LogisticRegression(max_iter=200)
    )
    pipeline.fit(x_train, y_train)

    raw_unlabeled = medium_dataframe.drop(columns=["subscribe"]).head(5)
    probabilities = pipeline.predict_proba(raw_unlabeled)[:, 1]
    assert probabilities.shape == (5,)
    assert ((probabilities >= 0) & (probabilities <= 1)).all()


def test_pipeline_handles_unseen_category(medium_dataframe):
    """OneHot 对未知类别必须忽略，保证上线健壮性。"""
    preprocessor = DataPreprocessor()
    feature_set = FeatureEngineer().transform(medium_dataframe)
    x_train, x_test, y_train, _ = preprocessor.split(feature_set)

    pipeline = preprocessor.build_pipeline(
        feature_set,
        LogisticRegression(max_iter=200),
    )
    pipeline.fit(x_train, y_train)

    unseen = x_test.head(1).copy()
    unseen["job"] = "a-brand-new-job"
    probability = pipeline.predict_proba(unseen)[0, 1]
    assert 0.0 <= probability <= 1.0
