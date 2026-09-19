"""数据集加载与校验实现。

职责：
1. 从 data/ 目录读取 train.csv / test.csv；
2. 按 schema.py 字段字典校验列完整性、校正数据类型；
3. 提供数据集元信息（行数、认购率等）。

注意：本模块不依赖 Streamlit，可独立单元测试。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.core.data_explorer import schema
from src.core.data_explorer.interfaces import (
    DataExplorerError,
    DatasetMeta,
    DatasetName,
    IDataLoader,
)
from src.utils.logger import get_logger, get_project_root

logger = get_logger(__name__)


class DataLoadingError(DataExplorerError):
    """数据加载或校验失败异常。"""


class CsvDataLoader(IDataLoader):
    """基于 CSV 文件的数据加载器。

    Attributes:
        data_dir: 数据目录，默认项目根目录下的 data/。
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else get_project_root() / "data"
        self._cache: dict[str, pd.DataFrame] = {}

    def _csv_path(self, dataset: str) -> Path:
        """返回数据集对应的 CSV 文件路径。"""
        return self.data_dir / f"{dataset}.csv"

    @staticmethod
    def _normalize_dataset_name(dataset: DatasetName | str) -> str:
        """将枚举或字符串统一转换为 train/test 小写名。"""
        name = (
            dataset.value if isinstance(dataset, DatasetName) else str(dataset).lower()
        )
        if name not in (DatasetName.TRAIN.value, DatasetName.TEST.value):
            raise DataLoadingError(
                f"不支持的数据集名称：{dataset}，仅允许 train 或 test"
            )
        return name

    def load(self, dataset: DatasetName | str) -> pd.DataFrame:
        """加载并校验数据集，结果在实例内缓存。

        Args:
            dataset: DatasetName.TRAIN / DatasetName.TEST 或字符串。

        Returns:
            pd.DataFrame: 类型校正后的数据副本。

        Raises:
            DataLoadingError: 文件缺失或字段不符合字段字典时抛出。
        """
        name = self._normalize_dataset_name(dataset)
        if name in self._cache:
            logger.debug("命中数据缓存：%s", name)
            return self._cache[name].copy()

        csv_path = self._csv_path(name)
        logger.info("开始加载数据集：%s", csv_path)
        if not csv_path.exists():
            message = f"数据文件不存在：{csv_path}"
            logger.error(message)
            raise DataLoadingError(message)

        try:
            data = pd.read_csv(csv_path)
        except Exception as exc:  # noqa: BLE001 - 读取失败需统一转为业务异常
            message = f"读取 CSV 失败：{csv_path}，原因：{exc}"
            logger.error(message)
            raise DataLoadingError(message) from exc

        data = self._validate_and_cast(data, name)
        self._cache[name] = data
        logger.success(
            "数据集 %s 加载完成，共 %d 行、%d 列", name, data.shape[0], data.shape[1]
        )
        return data.copy()

    def _validate_and_cast(self, data: pd.DataFrame, name: str) -> pd.DataFrame:
        """按字段字典校验列完整性并校正类型。"""
        expected_columns = (
            schema.ALL_COLUMNS
            if name == DatasetName.TRAIN.value
            else schema.TEST_COLUMNS
        )

        missing_columns = [
            column for column in expected_columns if column not in data.columns
        ]
        if missing_columns:
            message = f"数据集 {name} 缺失必需字段：{missing_columns}"
            logger.error(message)
            raise DataLoadingError(message)

        # 丢弃字段字典之外的意外列，保证下游处理稳定
        data = data[list(expected_columns)].copy()

        # 分类字段统一转为字符串并去除首尾空白；空值归入 unknown
        for column in schema.CATEGORICAL_COLUMNS:
            data[column] = (
                data[column].astype("string").str.strip().fillna(schema.UNKNOWN_TOKEN)
            )

        # 目标列同样规整为 yes/no 字符串
        if name == DatasetName.TRAIN.value:
            data[schema.TARGET_COLUMN] = (
                data[schema.TARGET_COLUMN].astype("string").str.strip().str.lower()
            )

        # 数值字段强制转数值，无法解析的置为缺失并记录警告
        for column in schema.NUMERIC_COLUMNS:
            original_missing = int(data[column].isna().sum())
            data[column] = pd.to_numeric(data[column], errors="coerce")
            current_missing = int(data[column].isna().sum())
            if current_missing > original_missing:
                logger.warning(
                    "字段 %s 存在 %d 个无法解析为数值的取值，已置为空值",
                    column,
                    current_missing - original_missing,
                )

        return data

    def describe(self, dataset: DatasetName | str) -> DatasetMeta:
        """返回数据集元信息。"""
        name = self._normalize_dataset_name(dataset)
        data = self.load(name)
        has_target = schema.TARGET_COLUMN in data.columns

        positive_count = None
        negative_count = None
        positive_rate = None
        if has_target:
            positive_count = int(
                (data[schema.TARGET_COLUMN] == schema.POSITIVE_LABEL).sum()
            )
            negative_count = int(
                (data[schema.TARGET_COLUMN] == schema.NEGATIVE_LABEL).sum()
            )
            total_labeled = positive_count + negative_count
            positive_rate = (
                round(positive_count / total_labeled, 4) if total_labeled else None
            )

        return DatasetMeta(
            name=name,
            row_count=int(data.shape[0]),
            column_count=int(data.shape[1]),
            has_target=has_target,
            positive_count=positive_count,
            negative_count=negative_count,
            positive_rate=positive_rate,
        )
