"""pytest 公共夹具：构造符合字段字典的小型合成数据集。

测试全部使用合成数据，既快又不依赖真实 CSV，CI 环境可直接运行。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.core.data_explorer import schema


def _build_rows() -> list[dict]:
    """构造 8 行覆盖多种取值的样本（3 人认购、5 人未认购）。"""
    rows = [
        # 基础模板，逐行覆盖不同分类与数值
        {
            "age": 30,
            "job": "admin.",
            "marital": "single",
            "education": "university.degree",
            "default": "no",
            "housing": "yes",
            "loan": "no",
            "contact": "cellular",
            "month": "may",
            "day_of_week": "mon",
            "duration": 120,
            "campaign": 1,
            "pdays": 999,
            "previous": 0,
            "poutcome": "nonexistent",
            "emp_var_rate": 1.1,
            "cons_price_index": 93.0,
            "cons_conf_index": -36.0,
            "lending_rate3m": 1.0,
            "nr_employed": 5100.0,
            "subscribe": "no",
        },
        {
            "age": 45,
            "job": "technician",
            "marital": "married",
            "education": "professional.course",
            "default": "unknown",
            "housing": "no",
            "loan": "yes",
            "contact": "cellular",
            "month": "aug",
            "day_of_week": "tue",
            "duration": 600,
            "campaign": 2,
            "pdays": 100,
            "previous": 2,
            "poutcome": "success",
            "emp_var_rate": -1.8,
            "cons_price_index": 94.0,
            "cons_conf_index": -40.0,
            "lending_rate3m": 1.5,
            "nr_employed": 5000.0,
            "subscribe": "yes",
        },
        {
            "age": 62,
            "job": "retired",
            "marital": "divorced",
            "education": "basic.9y",
            "default": "no",
            "housing": "no",
            "loan": "no",
            "contact": "telephone",
            "month": "oct",
            "day_of_week": "wed",
            "duration": 480,
            "campaign": 1,
            "pdays": 50,
            "previous": 1,
            "poutcome": "success",
            "emp_var_rate": -2.9,
            "cons_price_index": 92.5,
            "cons_conf_index": -42.0,
            "lending_rate3m": 0.8,
            "nr_employed": 4970.0,
            "subscribe": "yes",
        },
        {
            "age": 28,
            "job": "services",
            "marital": "single",
            "education": "high.school",
            "default": "no",
            "housing": "yes",
            "loan": "no",
            "contact": "cellular",
            "month": "may",
            "day_of_week": "thu",
            "duration": 90,
            "campaign": 7,
            "pdays": 999,
            "previous": 0,
            "poutcome": "nonexistent",
            "emp_var_rate": 1.4,
            "cons_price_index": 93.5,
            "cons_conf_index": -35.0,
            "lending_rate3m": 4.0,
            "nr_employed": 5220.0,
            "subscribe": "no",
        },
        {
            "age": 38,
            "job": "blue-collar",
            "marital": "married",
            "education": "basic.4y",
            "default": "no",
            "housing": "yes",
            "loan": "yes",
            "contact": "telephone",
            "month": "jun",
            "day_of_week": "fri",
            "duration": 200,
            "campaign": 3,
            "pdays": 999,
            "previous": 0,
            "poutcome": "nonexistent",
            "emp_var_rate": 1.4,
            "cons_price_index": 93.9,
            "cons_conf_index": -36.4,
            "lending_rate3m": 4.2,
            "nr_employed": 5228.0,
            "subscribe": "no",
        },
        {
            "age": 55,
            "job": "management",
            "marital": "married",
            "education": "university.degree",
            "default": "no",
            "housing": "no",
            "loan": "no",
            "contact": "cellular",
            "month": "mar",
            "day_of_week": "mon",
            "duration": 520,
            "campaign": 2,
            "pdays": 30,
            "previous": 3,
            "poutcome": "failure",
            "emp_var_rate": -0.1,
            "cons_price_index": 93.2,
            "cons_conf_index": -38.0,
            "lending_rate3m": 2.0,
            "nr_employed": 5050.0,
            "subscribe": "yes",
        },
        {
            "age": 24,
            "job": "student",
            "marital": "single",
            "education": "unknown",
            "default": "no",
            "housing": "unknown",
            "loan": "no",
            "contact": "cellular",
            "month": "dec",
            "day_of_week": "tue",
            "duration": 150,
            "campaign": 1,
            "pdays": 999,
            "previous": 0,
            "poutcome": "nonexistent",
            "emp_var_rate": -1.1,
            "cons_price_index": 94.2,
            "cons_conf_index": -46.2,
            "lending_rate3m": 1.3,
            "nr_employed": 4960.0,
            "subscribe": "no",
        },
        {
            "age": 41,
            "job": "unknown",
            "marital": "unknown",
            "education": "basic.6y",
            "default": "no",
            "housing": "yes",
            "loan": "unknown",
            "contact": "telephone",
            "month": "jul",
            "day_of_week": "wed",
            "duration": 300,
            "campaign": 6,
            "pdays": 200,
            "previous": 1,
            "poutcome": "failure",
            "emp_var_rate": 1.4,
            "cons_price_index": 94.0,
            "cons_conf_index": -39.0,
            "lending_rate3m": 4.5,
            "nr_employed": 5200.0,
            "subscribe": "no",
        },
    ]
    for index, row in enumerate(rows, start=1):
        row["id"] = index
    return rows


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """返回带目标列的 8 行合成 DataFrame。"""
    return pd.DataFrame(_build_rows(), columns=list(schema.ALL_COLUMNS))


@pytest.fixture
def sample_test_dataframe(sample_dataframe: pd.DataFrame) -> pd.DataFrame:
    """返回去掉目标列的“测试集”合成 DataFrame。"""
    return sample_dataframe.drop(columns=[schema.TARGET_COLUMN])


@pytest.fixture
def data_dir_with_csvs(
    tmp_path: Path, sample_dataframe: pd.DataFrame, sample_test_dataframe: pd.DataFrame
) -> Path:
    """在临时目录写入 train.csv / test.csv，返回目录路径。"""
    sample_dataframe.to_csv(tmp_path / "train.csv", index=False)
    sample_test_dataframe.to_csv(tmp_path / "test.csv", index=False)
    return tmp_path


@pytest.fixture
def medium_dataframe() -> pd.DataFrame:
    """构造 240 行带标签规律的合成数据（M2 模型训练测试用）。

    认购标签与 poutcome/month/contact/campaign 强相关，
    保证模型能在小数据上学到信号；固定随机种子保证可复现。
    """
    import numpy as np

    rng = np.random.RandomState(42)
    jobs = ("admin.", "technician", "retired", "services", "blue-collar", "student")
    months = ("may", "jul", "aug", "oct", "mar", "dec")
    rows: list[dict] = []
    for index in range(240):
        poutcome = rng.choice(
            ("success", "failure", "nonexistent"), p=(0.2, 0.25, 0.55)
        )
        month = str(rng.choice(months))
        contact = str(rng.choice(("cellular", "telephone"), p=(0.6, 0.4)))
        campaign = int(rng.choice((1, 2, 3, 6, 8), p=(0.4, 0.25, 0.15, 0.1, 0.1)))

        # 确定性业务规律 + 少量噪声
        positive_prob = 0.08
        if poutcome == "success":
            positive_prob += 0.45
        if month in ("mar", "oct", "dec"):
            positive_prob += 0.2
        if contact == "cellular":
            positive_prob += 0.1
        if campaign >= 6:
            positive_prob -= 0.15
        label = "yes" if rng.rand() < positive_prob else "no"

        rows.append(
            {
                "id": index + 1,
                "age": int(rng.randint(20, 70)),
                "job": str(rng.choice(jobs)),
                "marital": str(rng.choice(("single", "married", "divorced"))),
                "education": str(
                    rng.choice(("basic.9y", "high.school", "university.degree"))
                ),
                "default": "no",
                "housing": str(rng.choice(("yes", "no"))),
                "loan": "no",
                "contact": contact,
                "month": month,
                "day_of_week": str(rng.choice(("mon", "tue", "wed", "thu", "fri"))),
                "duration": int(rng.randint(60, 900)),
                "campaign": campaign,
                "pdays": (
                    999 if poutcome == "nonexistent" else int(rng.randint(10, 300))
                ),
                "previous": 0 if poutcome == "nonexistent" else int(rng.randint(1, 4)),
                "poutcome": poutcome,
                "emp_var_rate": round(float(rng.uniform(-3.0, 1.5)), 1),
                "cons_price_index": round(float(rng.uniform(92.0, 94.5)), 1),
                "cons_conf_index": round(float(rng.uniform(-46.0, -35.0)), 1),
                "lending_rate3m": round(float(rng.uniform(0.8, 4.5)), 2),
                "nr_employed": round(float(rng.uniform(4950.0, 5230.0)), 1),
                "subscribe": label,
            }
        )
    return pd.DataFrame(rows, columns=list(schema.ALL_COLUMNS))
