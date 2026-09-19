"""特征工程实现。

职责：
1. 从原始宽表生成建模特征（含业务衍生特征）；
2. 按配置隔离 duration 数据泄露特征（DEC-008）；
3. 产出并落盘字段映射表 db/field_mapping.json，作为数据血缘依据。

注意：本模块只做 DataFrame 层面的特征构造；OneHot/标准化等
带状态的变换由 preprocessing.py 中的 sklearn 流水线负责。
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.core.data_explorer import schema
from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.interfaces import (
    FeatureSet,
    IFeatureEngineer,
    ModelTrainingError,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 年龄分箱边界与中文标签
_AGE_BINS = (0, 30, 45, 60, 200)
_AGE_LABELS = ("青年(<=30)", "中年(31-45)", "中老年(46-60)", "老年(>60)")

# 衍生特征中文说明（字段映射表使用）
_DERIVED_DESCRIPTIONS: dict[str, str] = {
    "is_ever_contacted": "是否曾被历史营销联系过（pdays 非 999）",
    "is_high_frequency": "本次活动是否高频触达（campaign 达到阈值）",
    "was_previous_success": "上次营销是否成功（poutcome=success）",
    "contact_cellular": "本次是否通过手机联系（contact=cellular）",
    "age_bucket": "年龄分箱（业务可解释分段）",
}


class FeatureEngineer(IFeatureEngineer):
    """基于业务规则的特征工程器。"""

    def __init__(self, config: ModelTrainingConfig | None = None) -> None:
        self.config = config or ModelTrainingConfig()

    def transform(self, raw: pd.DataFrame) -> FeatureSet:
        """执行特征工程，返回建模宽表与特征清单。

        Raises:
            ModelTrainingError: 缺少建模必需字段时抛出中文异常。
        """
        logger.info("开始特征工程，输入 %d 行、%d 列", raw.shape[0], raw.shape[1])
        data = raw.copy()

        required = [
            schema.ID_COLUMN,
            *schema.CATEGORICAL_COLUMNS,
            *schema.NUMERIC_COLUMNS,
        ]
        missing = [column for column in required if column not in data.columns]
        if missing:
            message = f"特征工程输入缺少必需字段：{missing}"
            logger.error(message)
            raise ModelTrainingError(message)

        # 标识列不参与建模
        data = data.drop(columns=[schema.ID_COLUMN])

        # duration 数据泄露隔离：默认剔除
        if not self.config.include_duration and "duration" in data.columns:
            data = data.drop(columns=["duration"])
            logger.warning("已按配置隔离事后特征 duration，防止数据泄露（DEC-008）")

        data = self._add_derived_features(data)

        # 目标列不进特征清单
        target = schema.TARGET_COLUMN
        categorical = tuple(
            column
            for column in (schema.CATEGORICAL_COLUMNS + ("age_bucket",))
            if column in data.columns and column != target
        )
        numeric_source = tuple(
            column for column in schema.NUMERIC_COLUMNS if column in data.columns
        )
        derived_binary = (
            "is_ever_contacted",
            "is_high_frequency",
            "was_previous_success",
            "contact_cellular",
        )
        numeric = tuple(
            column
            for column in (*numeric_source, *derived_binary)
            if column in data.columns and column != target
        )

        feature_set = FeatureSet(
            data=data,
            categorical_features=categorical,
            numeric_features=numeric,
            target=target,
        )
        logger.success(
            "特征工程完成：%d 个分类特征、%d 个数值特征，宽表共 %d 列",
            len(categorical),
            len(numeric),
            data.shape[1],
        )
        return feature_set

    def _add_derived_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """添加业务衍生特征。"""
        # 是否曾被联系：pdays=999 表示从未联系
        data["is_ever_contacted"] = (
            data["pdays"] != self.config.pdays_never_contacted
        ).astype(int)

        # 是否高频触达：超过阈值视为过度营销
        data["is_high_frequency"] = (
            data["campaign"] >= self.config.high_frequency_threshold
        ).astype(int)

        # 上次营销成功标记
        data["was_previous_success"] = (data["poutcome"] == "success").astype(int)

        # 手机联系标记
        data["contact_cellular"] = (data["contact"] == "cellular").astype(int)

        # 年龄分箱（保留原 age 数值列，额外增加可解释分类列）
        data["age_bucket"] = pd.cut(
            data["age"],
            bins=_AGE_BINS,
            labels=_AGE_LABELS,
            right=True,
        ).astype(str)

        logger.info(
            "已生成 %d 个衍生特征：is_ever_contacted/is_high_frequency/"
            "was_previous_success/contact_cellular/age_bucket",
            5,
        )
        return data

    def build_field_mapping(self, feature_set: FeatureSet) -> dict:
        """生成字段映射表（原始字段 -> 衍生特征 -> 编码方式 -> 建模去向）。"""
        used_raw_numeric = [
            column
            for column in schema.NUMERIC_COLUMNS
            if column in feature_set.data.columns or column == "duration"
        ]
        mapping = {
            "版本": "v2.0",
            "生成时间": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "目标字段": {
                "字段名": schema.TARGET_COLUMN,
                "编码": {"no": 0, "yes": 1},
                "说明": "二分类目标，yes=认购定期存款",
            },
            "剔除字段": {
                "id": "记录唯一标识，无业务含义，不参与建模",
                **(
                    {
                        "duration": (
                            "事后特征（通话结束后才可知），默认隔离防泄露（DEC-008）；"
                            "include_duration=True 时可用于对照实验"
                        )
                    }
                    if not self.config.include_duration
                    else {}
                ),
            },
            "原始数值字段": {
                column: {
                    "中文名": schema.COLUMN_DESCRIPTIONS[column][0],
                    "处理方式": "StandardScaler 标准化",
                    "是否进入模型": column in feature_set.numeric_features,
                }
                for column in used_raw_numeric
            },
            "原始分类字段": {
                column: {
                    "中文名": schema.COLUMN_DESCRIPTIONS[column][0],
                    "处理方式": "OneHotEncoder（handle_unknown=ignore）",
                    "是否进入模型": column in feature_set.categorical_features,
                }
                for column in schema.CATEGORICAL_COLUMNS
            },
            "衍生特征": {
                name: {
                    "中文名": description,
                    "类型": "categorical" if name == "age_bucket" else "binary",
                    "处理方式": (
                        "OneHot 编码"
                        if name == "age_bucket"
                        else "0/1 数值，随数值列标准化"
                    ),
                }
                for name, description in _DERIVED_DESCRIPTIONS.items()
            },
            "建模特征清单": {
                "categorical": list(feature_set.categorical_features),
                "numeric": list(feature_set.numeric_features),
            },
        }
        return mapping

    def save_field_mapping(self, mapping: dict, path: Path) -> None:
        """以 UTF-8 JSON 落盘字段映射表。"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(mapping, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.success("字段映射表已保存：%s", path)
