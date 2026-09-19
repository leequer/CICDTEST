"""动态筛选实现。

支持：
- 分类字段多选（job / marital / housing / contact / month 等）；
- 数值字段区间筛选（age / duration / campaign 等）；
- 训练集额外支持按目标字段 subscribe 筛选。

筛选条件以 FilterCriteria 契约表达，前端控件与业务逻辑解耦。
"""

from __future__ import annotations

import pandas as pd

from src.core.data_explorer import schema
from src.core.data_explorer.interfaces import (
    DataExplorerError,
    FilterCriteria,
    IDataFilter,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataFilter(IDataFilter):
    """基于 pandas 的动态筛选器。"""

    def apply(self, data: pd.DataFrame, criteria: FilterCriteria) -> pd.DataFrame:
        """按筛选条件返回过滤后的数据副本。

        分类字段：选中值为空列表表示不限制；
        数值字段：取闭区间 [最小值, 最大值]，空值记录不参与区间命中。
        """
        self._validate_columns(data, criteria)
        mask = pd.Series(True, index=data.index)

        for column, selected_values in criteria.categorical_selections.items():
            if not selected_values:
                continue
            mask &= data[column].isin(selected_values)
            logger.debug(
                "分类筛选 %s in %s，剩余 %d 行",
                column,
                selected_values,
                int(mask.sum()),
            )

        for column, value_range in criteria.numeric_ranges.items():
            if value_range is None:
                continue
            lower, upper = value_range
            column_mask = (data[column] >= lower) & (data[column] <= upper)
            # 空值不命中数值区间
            mask &= column_mask.fillna(False)
            logger.debug(
                "数值筛选 %s in [%s, %s]，剩余 %d 行",
                column,
                lower,
                upper,
                int(mask.sum()),
            )

        filtered = data.loc[mask].copy()
        logger.info(
            "动态筛选完成：原始 %d 行 -> 筛选后 %d 行（保留 %.2f%%）",
            int(data.shape[0]),
            int(filtered.shape[0]),
            (filtered.shape[0] / data.shape[0] * 100) if data.shape[0] else 0.0,
        )
        return filtered

    @staticmethod
    def _validate_columns(data: pd.DataFrame, criteria: FilterCriteria) -> None:
        """校验筛选条件引用的字段是否真实存在。"""
        unknown = [
            column
            for column in (
                *criteria.categorical_selections.keys(),
                *criteria.numeric_ranges.keys(),
            )
            if column not in data.columns
        ]
        if unknown:
            message = f"筛选条件引用了数据中不存在的字段：{unknown}"
            logger.error(message)
            raise DataExplorerError(message)

    def default_criteria(self, data: pd.DataFrame) -> FilterCriteria:
        """生成默认条件：所有分类字段全选、所有数值字段取完整区间。"""
        criteria = FilterCriteria(
            categorical_selections={
                column: list(values)
                for column, values in self.categorical_options(data).items()
            },
            numeric_ranges={
                column: bounds for column, bounds in self.numeric_bounds(data).items()
            },
        )
        logger.debug("已生成默认筛选条件（不限制任何字段）")
        return criteria

    def categorical_options(self, data: pd.DataFrame) -> dict[str, list[str]]:
        """返回各分类字段可选值；有自然顺序的字段按业务顺序排列，其余按频次降序。"""
        columns = list(schema.CATEGORICAL_COLUMNS)
        if schema.TARGET_COLUMN in data.columns:
            columns.append(schema.TARGET_COLUMN)

        options: dict[str, list[str]] = {}
        for column in columns:
            if column not in data.columns:
                continue
            actual_values = set(data[column].dropna().unique().tolist())
            ordered = schema.ORDERED_CATEGORIES.get(column)
            if ordered is not None:
                values = [value for value in ordered if value in actual_values]
                # 兜底：数据中出现但业务顺序表未覆盖的取值，追加在末尾
                values.extend(sorted(actual_values - set(values)))
            else:
                # 按出现频次降序，频次相同按字母序，保证结果稳定
                counts = data[column].value_counts()
                values = sorted(
                    actual_values, key=lambda value: (-counts[value], value)
                )
            options[column] = values
        return options

    def numeric_bounds(self, data: pd.DataFrame) -> dict[str, tuple[float, float]]:
        """返回数值字段（含 id）的最小/最大边界。"""
        columns = (schema.ID_COLUMN, *schema.NUMERIC_COLUMNS)
        bounds: dict[str, tuple[float, float]] = {}
        for column in columns:
            if column not in data.columns:
                continue
            series = pd.to_numeric(data[column], errors="coerce").dropna()
            if series.empty:
                continue
            bounds[column] = (float(series.min()), float(series.max()))
        return bounds
