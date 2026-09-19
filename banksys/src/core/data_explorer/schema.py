"""银行营销数据集字段字典与元数据定义。

数据来源：阿里云天池「银行营销数据集」（基于葡萄牙银行电话营销公开数据改版）。
本模块是全项目唯一的字段事实来源，加载、筛选、图表、洞察均以此为准。
"""

from __future__ import annotations

# 标识列
ID_COLUMN = "id"

# 目标列（二分类标签：客户是否认购定期存款）
TARGET_COLUMN = "subscribe"
POSITIVE_LABEL = "yes"
NEGATIVE_LABEL = "no"

# 分类列中的缺失占位符（天池数据以字符串 unknown 表示未知，而非空值）
UNKNOWN_TOKEN = "unknown"

# pdays=999 表示“此前从未联系过该客户”（行业通用哨兵值）
PDAYS_NEVER_CONTACTED = 999

# 分类字段
CATEGORICAL_COLUMNS: tuple[str, ...] = (
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
)

# 目标列单独管理，不参与普通特征筛选
TARGET_VALUES: tuple[str, ...] = (NEGATIVE_LABEL, POSITIVE_LABEL)

# 数值字段
NUMERIC_COLUMNS: tuple[str, ...] = (
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
)

# 具有自然业务顺序的分类字段及其展示顺序
ORDERED_CATEGORIES: dict[str, tuple[str, ...]] = {
    "month": (
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ),
    "day_of_week": ("mon", "tue", "wed", "thu", "fri"),
    "education": (
        "unknown",
        "illiterate",
        "basic.4y",
        "basic.6y",
        "basic.9y",
        "high.school",
        "professional.course",
        "university.degree",
    ),
    TARGET_COLUMN: (NEGATIVE_LABEL, POSITIVE_LABEL),
}

# 二值（yes/no/unknown）字段，前端可使用精简选项
BINARY_LIKE_COLUMNS: tuple[str, ...] = ("default", "housing", "loan")

# 训练集完整字段顺序（共 22 列，含目标列）
ALL_COLUMNS: tuple[str, ...] = (
    "id",
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
    TARGET_COLUMN,
)

# 测试集字段（无目标列）
TEST_COLUMNS: tuple[str, ...] = tuple(
    column for column in ALL_COLUMNS if column != TARGET_COLUMN
)

# 字段中文数据字典：字段名 -> (中文名, 业务含义)
COLUMN_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "id": ("客户编号", "数据集中客户的唯一标识，无业务含义"),
    "age": ("年龄", "客户年龄（岁）"),
    "job": ("职业", "客户的职业类型，unknown 表示未知"),
    "marital": ("婚姻状况", "已婚 / 单身 / 离异，unknown 表示未知"),
    "education": ("受教育程度", "学历层级，按 basic.4y 到 university.degree 递进"),
    "default": ("是否有违约记录", "信用违约记录：yes/no/unknown"),
    "housing": ("是否有住房贷款", "住房贷款状态：yes/no/unknown"),
    "loan": ("是否有个人贷款", "个人贷款状态：yes/no/unknown"),
    "contact": ("联系方式", "本次营销联系方式：cellular 手机 / telephone 座机"),
    "month": ("最后联系月份", "本年度最后一次联系的月份"),
    "day_of_week": ("最后联系星期", "最后一次联系当天是星期几"),
    "duration": (
        "通话时长",
        "本次营销通话持续时长；属事后特征，上线前不可用于预测。本数据集数值整体偏大，单位口径需与业务方核对",
    ),
    "campaign": ("本次营销联系次数", "本次活动中对该客户的联系次数"),
    "pdays": ("距上次联系天数", "距上一次活动联系该客户经过的天数；999 表示从未联系过"),
    "previous": ("历史营销联系次数", "本次活动之前对该客户的联系次数"),
    "poutcome": ("上次营销结果", "上一次营销活动结果：success/failure/nonexistent"),
    "emp_var_rate": ("就业变动率", "季度宏观经济指标：就业变动率"),
    "cons_price_index": ("消费者价格指数", "季度宏观经济指标：居民消费价格指数"),
    "cons_conf_index": ("消费者信心指数", "季度宏观经济指标：消费者信心指数"),
    "lending_rate3m": ("三个月拆借利率", "三个月期银行间同业拆借利率"),
    "nr_employed": ("就业人数", "季度社会就业人数（千人）"),
    TARGET_COLUMN: ("是否认购", "目标变量：yes 认购定期存款 / no 未认购"),
}
