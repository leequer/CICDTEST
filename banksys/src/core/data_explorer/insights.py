"""特征洞察报告生成器。

基于（可被用户动态筛选后的）数据，自动产出业务洞察、数据质量结论、
特征工程与建模提示。所有结论均带量化证据，供仪表盘“特征洞察报告”页展示。
"""

from __future__ import annotations

import pandas as pd

from src.core.data_explorer import schema
from src.core.data_explorer.interfaces import (
    IInsightGenerator,
    InsightCategory,
    InsightItem,
    InsightLevel,
    InsightReport,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 小样本阈值：分组样本低于该值时，转化率结论不具代表性
_MIN_SAMPLE_SIZE = 30


class InsightGenerator(IInsightGenerator):
    """根据 pandas 数据自动生成特征洞察。"""

    def generate(
        self, data: pd.DataFrame, dataset_name: str = "train"
    ) -> InsightReport:
        """生成洞察报告；测试集等无标签数据仅产出数据质量类结论。"""
        logger.info("开始生成特征洞察报告，当前样本 %d 行", int(data.shape[0]))
        items: list[InsightItem] = []
        positive_rate = None
        has_target = schema.TARGET_COLUMN in data.columns

        if data.empty:
            items.append(
                InsightItem(
                    title="当前筛选条件下没有样本",
                    category=InsightCategory.DATA_QUALITY,
                    level=InsightLevel.WARN,
                    content="请放宽侧边栏筛选条件后再查看洞察结论。",
                )
            )
            return InsightReport(
                dataset_name=dataset_name,
                row_count=0,
                positive_rate=None,
                items=items,
            )

        # 数据质量类洞察（有无标签均可生成）
        items.extend(self._quality_insights(data))

        if has_target:
            positive_series = data[schema.TARGET_COLUMN] == schema.POSITIVE_LABEL
            positive_rate = round(float(positive_series.mean()), 4)
            items.insert(
                0,
                InsightItem(
                    title="整体认购率概览",
                    category=InsightCategory.BUSINESS,
                    level=InsightLevel.INFO,
                    content=(
                        f"当前筛选范围内共 {len(data)} 名客户，"
                        f"其中 {int(positive_series.sum())} 人认购，"
                        f"整体认购率 {positive_rate:.2%}，属于典型不平衡分类问题。"
                    ),
                    metrics={
                        "样本数": str(len(data)),
                        "认购人数": str(int(positive_series.sum())),
                        "认购率": f"{positive_rate:.2%}",
                    },
                ),
            )
            items.extend(self._business_insights(data))
            items.extend(self._feature_insights(data, positive_series))

        logger.success("特征洞察报告生成完成，共 %d 条结论", len(items))
        return InsightReport(
            dataset_name=dataset_name,
            row_count=int(data.shape[0]),
            positive_rate=positive_rate,
            items=items,
        )

    def _quality_insights(self, data: pd.DataFrame) -> list[InsightItem]:
        """数据质量类洞察：unknown 缺失、pdays 哨兵值。"""
        items: list[InsightItem] = []

        # 分类字段 unknown 占比
        unknown_rates = {}
        for column in schema.CATEGORICAL_COLUMNS:
            if column not in data.columns:
                continue
            rate = float((data[column] == schema.UNKNOWN_TOKEN).mean())
            if rate > 0:
                unknown_rates[column] = rate
        if unknown_rates:
            worst_column = max(unknown_rates, key=lambda col: unknown_rates[col])
            chinese_name = schema.COLUMN_DESCRIPTIONS[worst_column][0]
            items.append(
                InsightItem(
                    title=f"字段「{chinese_name}」unknown 占比最高",
                    category=InsightCategory.DATA_QUALITY,
                    level=(
                        InsightLevel.WARN
                        if unknown_rates[worst_column] > 0.1
                        else InsightLevel.INFO
                    ),
                    content=(
                        f"{chinese_name}（{worst_column}）存在 "
                        f"{unknown_rates[worst_column]:.2%} 的 unknown 取值，"
                        "建模时建议作为独立类别保留，或评估插补/剔除方案。"
                    ),
                    metrics={
                        "字段": worst_column,
                        "unknown占比": f"{unknown_rates[worst_column]:.2%}",
                    },
                )
            )

        # pdays=999 哨兵值说明
        if "pdays" in data.columns:
            never_rate = float((data["pdays"] == schema.PDAYS_NEVER_CONTACTED).mean())
            items.append(
                InsightItem(
                    title="pdays=999 表示此前从未联系，需特征化处理",
                    category=InsightCategory.DATA_QUALITY,
                    level=InsightLevel.SUGGEST,
                    content=(
                        f"有 {never_rate:.2%} 的客户 pdays 为 999"
                        "（从未被历史营销联系）。"
                        "直接作为数值输入会误导模型，"
                        "建议派生「是否曾被联系」二值特征，并将 999 单独处理。"
                    ),
                    metrics={"从未联系客户占比": f"{never_rate:.2%}"},
                )
            )

        return items

    def _business_insights(self, data: pd.DataFrame) -> list[InsightItem]:
        """业务类洞察：关键分类字段的认购率差异。"""
        items: list[InsightItem] = []
        key_columns = ("poutcome", "month", "contact", "job")
        for column in key_columns:
            if column not in data.columns:
                continue
            grouped = (
                data.groupby(column)[schema.TARGET_COLUMN]
                .agg(
                    sample_count="count",
                    positive_rate=lambda series: float(
                        (series == schema.POSITIVE_LABEL).mean()
                    ),
                )
                .reset_index()
            )
            grouped = grouped[grouped["sample_count"] >= _MIN_SAMPLE_SIZE]
            if len(grouped) < 2:
                continue

            best_row = grouped.loc[grouped["positive_rate"].idxmax()]
            worst_row = grouped.loc[grouped["positive_rate"].idxmin()]
            lift = (
                best_row["positive_rate"] / worst_row["positive_rate"]
                if worst_row["positive_rate"] > 0
                else float("inf")
            )
            chinese_name = schema.COLUMN_DESCRIPTIONS[column][0]
            content = (
                f"「{best_row[column]}」客户群认购率最高（{best_row['positive_rate']:.2%}），"
                f"「{worst_row[column]}」最低（{worst_row['positive_rate']:.2%}），"
                f"相差约 {lift:.1f} 倍。营销资源可优先向高转化客群倾斜。"
            )
            items.append(
                InsightItem(
                    title=f"{chinese_name}（{column}）对认购率有明显区分度",
                    category=InsightCategory.BUSINESS,
                    level=InsightLevel.INFO,
                    content=content,
                    metrics={
                        "最高分组": (
                            f"{best_row[column]} " f"{best_row['positive_rate']:.2%}"
                        ),
                        "最低分组": (
                            f"{worst_row[column]} " f"{worst_row['positive_rate']:.2%}"
                        ),
                    },
                )
            )
        return items

    def _feature_insights(
        self, data: pd.DataFrame, positive_series: pd.Series
    ) -> list[InsightItem]:
        """特征工程与建模提示：数据泄露、数值相关性。"""
        items: list[InsightItem] = []

        # 数据泄露红线：duration
        if "duration" in data.columns:
            subscribed_mean = float(data.loc[positive_series, "duration"].mean())
            unsubscribed_mean = float(data.loc[~positive_series, "duration"].mean())
            items.append(
                InsightItem(
                    title="红线提示：duration（通话时长）是事后特征，禁止直接用于上线预测",
                    category=InsightCategory.MODELING,
                    level=InsightLevel.WARN,
                    content=(
                        "通话时长只有在通话结束后才能确定，用它预测“是否认购”属于数据泄露，"
                        "上线建模前必须剔除，或仅用于通话过程中的实时干预场景。"
                        f"当前数据中认购客户平均 {subscribed_mean:.0f}、"
                        f"未认购客户平均 {unsubscribed_mean:.0f}，差异有限，"
                        "且数值整体偏大、单位口径存疑，建模前需与业务方核对。"
                    ),
                    metrics={
                        "认购客户平均时长": f"{subscribed_mean:.0f}",
                        "未认购客户平均时长": f"{unsubscribed_mean:.0f}",
                    },
                )
            )

        # 数值特征与标签相关性排行
        numeric_columns = [
            column for column in schema.NUMERIC_COLUMNS if column in data.columns
        ]
        correlations = {}
        encoded_target = positive_series.astype(int)
        for column in numeric_columns:
            series = pd.to_numeric(data[column], errors="coerce")
            valid = series.notna()
            if valid.sum() < _MIN_SAMPLE_SIZE or series[valid].std() == 0:
                continue
            correlations[column] = float(series[valid].corr(encoded_target[valid]))

        if correlations:
            ranked = sorted(
                correlations.items(), key=lambda item: abs(item[1]), reverse=True
            )
            top_columns = ranked[:3]
            lines = "；".join(
                f"{schema.COLUMN_DESCRIPTIONS[column][0]}（{column}）"
                f"相关系数 {value:+.3f}"
                for column, value in top_columns
            )
            items.append(
                InsightItem(
                    title="与认购结果相关性最强的数值特征",
                    category=InsightCategory.FEATURE,
                    level=InsightLevel.SUGGEST,
                    content=(
                        f"按皮尔逊相关系数绝对值排序，Top3 为：{lines}。"
                        "这些字段值得优先进行分箱、标准化等特征工程，"
                        "但相关不等于因果，且需结合业务剔除数据泄露特征。"
                    ),
                    metrics={column: f"{value:+.3f}" for column, value in top_columns},
                )
            )

        # 营销触达次数建议
        if "campaign" in data.columns:
            high_frequency = data["campaign"] >= 6
            if bool(high_frequency.any()):
                high_rate = float(positive_series[high_frequency].mean())
                low_rate = float(positive_series[~high_frequency].mean())
                items.append(
                    InsightItem(
                        title="过度触达客户的认购率明显走低",
                        category=InsightCategory.BUSINESS,
                        level=InsightLevel.SUGGEST,
                        content=(
                            f"本次活动联系 6 次及以上的客户认购率仅 {high_rate:.2%}，"
                            f"低于 6 次以内客户的 {low_rate:.2%}。"
                            "建议设定触达上限，减少无效电话骚扰并节约营销成本。"
                        ),
                        metrics={
                            "高频触达认购率": f"{high_rate:.2%}",
                            "常规触达认购率": f"{low_rate:.2%}",
                        },
                    )
                )

        return items
