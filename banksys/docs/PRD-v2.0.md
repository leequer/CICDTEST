# 产品需求文档 PRD-v2.0 —— banksys 银行电话营销智能分析

| 项目 | 内容 |
|---|---|
| 文档版本 | v2.0（首版） |
| 创建日期 | 2026-09-19 |
| 应用名称 | banksys |
| 所属仓库 | https://github.com/leequer/CICDTEST （多应用仓库，banksys 为子目录应用） |
| 数据来源 | 阿里云天池「银行营销数据集」（葡萄牙银行电话营销数据改版） |
| 规范依据 | standards/ 目录下实际存在的 00-09 系列规范（02 项目结构、08 代码风格、04 GitHub Actions 模板、05 Lessons Learned 等）。任务中点名的 *-v2.0 规范文件在仓库中不存在，本 PRD 按约定的 10 章节结构编写，偏差详见 PROJECT-DECISION-LOG-v2.0.md DEC-001 |

---

## 第 1 章 项目概述

### 1.1 业务背景

银行定期存款营销长期依赖电话外呼（Telemarketing）。传统"广撒网"式营销存在三大痛点：

1. **成本高**：每一通电话都消耗坐席工时与通讯成本；
2. **转化率低**：训练集 22,500 名客户中仅 2,952 人认购，整体认购率 **13.12%**，超 86% 的电话是无效触达；
3. **客户体验差**：对无意向客户反复外呼形成骚扰（数据中 11.08% 的客户被联系 6 次及以上）。

### 1.2 项目愿景与目标

以历史营销数据为基础，构建"数据 → 洞察 → 模型 → 在线预测"的全链路 AI 应用，实现**精准营销**：提前识别高潜力客户、优化营销资源分配、提升认购率并降低无效骚扰。

项目分阶段推进：

| 阶段 | 名称 | 目标 |
|---|---|---|
| M1（本次） | 数据分析交互性 | 交互式数据探索仪表盘：动态筛选、可视化分析、自动特征洞察 |
| M2 | 特征工程与建模 | 可复现训练管线、基线模型、模型评估 |
| M3 | 在线预测服务 | API + 批量预测、模型版本管理 |
| M4 | CI/CD 与部署 | CI 已在 M1 落地；CD/容器化按需推进 |

### 1.3 本期（M1）范围

**做**：Streamlit 交互式仪表盘，覆盖 train.csv（22,500 行/22 列，含标签）与 test.csv（7,500 行/21 列，无标签），实现全字段动态筛选、Plotly 可视化、特征洞察报告与 JSON 导出、GitHub Actions CI。

**不做**：模型训练、在线预测 API、数据库持久化、CD 自动部署。

### 1.4 核心价值指标

| 指标 | 口径 | 目标 |
|---|---|---|
| 分析效率 | 业务人员自助完成一次"客群对比分析"耗时 | 由小时级降至 5 分钟内 |
| 字段覆盖 | 可动态筛选字段 / 全部 22 个字段 | 100% |
| 洞察可用性 | 自动生成的洞察条目数 | 不少于 8 条且含量化证据 |
| 工程质量 | CI 门禁（black/ruff/pytest，覆盖率） | 100% 通过，覆盖率 ≥ 80%（实测 92%） |

---

## 第 2 章 干系人与用户故事

### 2.1 干系人

| 角色 | 关注点 |
|---|---|
| 银行业务分析师（主要用户） | 自助筛选客群、发现认购规律、导出洞察报告 |
| 营销运营经理 | 哪些客群值得优先触达、触达次数上限建议 |
| 算法工程师（后续阶段） | 数据质量结论、特征-标签关系、数据泄露红线提示 |
| 项目维护者 | CI 健康、代码规范、可复现的本地运行环境 |

### 2.2 用户故事（本期验收依据）

- **US-01**：作为分析师，我希望在侧边栏对 age/job/marital/housing/contact/month 等**全部字段**进行动态筛选，以便聚焦任意客群。
- **US-02**：作为分析师，我希望一键切换训练集/测试集，并明确知道测试集没有认购标签。
- **US-03**：作为分析师，我希望查看目标变量认购率分布，快速感知类别不平衡程度。
- **US-04**：作为分析师，我希望查看任意分类字段与数值字段的分布图，并可按"认购/未认购"分组对比。
- **US-05**：作为分析师，我希望查看数值特征相关性热图，快速发现共线性与标签关联。
- **US-06**：作为分析师，我希望对比任意字段下各组客户的认购率（分类看柱状、数值看分箱趋势）。
- **US-07**：作为分析师，我希望系统自动产出带量化证据的特征洞察报告（业务洞察、数据质量、特征工程、建模提示），并能导出 JSON。
- **US-08**：作为分析师，我希望重置按钮一键恢复默认筛选。
- **US-09**：作为维护者，我希望每次推送由 CI 自动完成格式、风格与单元测试门禁。

---

## 第 3 章 功能需求

| 编号 | 功能 | 描述 | 优先级 | 对应故事 |
|---|---|---|---|---|
| FR-01 | 数据集切换 | 侧边栏单选 train/test；无标签数据集自动禁用认购类分析并给出中文提示 | P0 | US-02 |
| FR-02 | 全字段动态筛选 | 10 个分类字段（含 subscribe）多选 + 11 个数值字段（含 id）区间滑块；默认全选/全区间；空选=不限制 | P0 | US-01/US-08 |
| FR-03 | 顶部 KPI | 原始样本量、筛选后样本量、保留比例、筛选后认购率（含认购人数） | P0 | US-01 |
| FR-04 | 数据概览 | 目标分布图、数据质量（unknown/缺失）图、字段数据字典、明细预览（前 500 行） | P0 | US-03 |
| FR-05 | 字段分布分析 | 分类柱状/数值直方图，支持按认购结果分组着色 | P0 | US-04 |
| FR-06 | 相关性热图 | 10 个数值字段 + subscribe 编码（yes=1）的皮尔逊相关矩阵 | P0 | US-05 |
| FR-07 | 认购率分组对比 | 分类字段各组认购率柱图（悬停样本量）；数值字段等频分箱认购率折线（档数 3-10 可调） | P0 | US-06 |
| FR-08 | 特征洞察报告 | 自动生成信息/建议/风险三级、四类（业务/质量/特征/建模）洞察，含量化证据与 JSON 导出 | P0 | US-07 |
| FR-09 | 中文与日志 | 界面/注释/日志全简体中文；终端 rich 彩色日志（DEBUG 暗白、INFO 青、SUCCESS 绿、WARNING 黄、ERROR 红、CRITICAL 白字红底） | P0 | 规范 |
| FR-10 | CI 门禁 | push/PR 触发 black --check、ruff check、pytest（覆盖率门槛 80%）；多应用仓库 paths 隔离 | P0 | US-09 |
| FR-11 | 小样本保护 | 分组认购率结论仅在组样本 ≥ 30 时采用，避免偶然结论 | P1 | US-07 |
| FR-12 | 异常中文提示 | 文件缺失、字段缺失、字段名非法、无标签分析等均抛出/展示中文可读信息 | P0 | 规范 |

---

## 第 4 章 非功能需求

| 类别 | 要求 |
|---|---|
| 性能 | 22,500 行数据首次加载 ≤ 3 秒；筛选交互到图表刷新 ≤ 1 秒（本地 Streamlit 缓存） |
| 兼容性 | Python 3.10（统一虚拟环境 envbank）；Windows 本地运行，CI 运行于 ubuntu-latest；路径一律 pathlib |
| 可维护性 | 遵循 standards/08-CODE-STYLE：PEP 8、black 88 列、绝对导入、简体中文注释、禁止 emoji |
| 可测试性 | 核心业务逻辑不依赖 Streamlit；单元测试使用合成数据，无需真实 CSV 即可在 CI 运行 |
| 可移植性 | 跨平台换行符由 .gitattributes 统一为 LF；不硬编码绝对路径 |
| 安全 | 不打印 Token/密钥；数据仅为脱敏营销统计字段，不含姓名、账号、手机号 |
| 可观测 | 关键流程（加载、筛选、洞察生成）输出 rich 中文日志并带文件位置 |

---

## 第 5 章 数据需求与数据库模型

### 5.1 数据资产现状

| 文件 | 行数 | 列数 | 含标签 | 大小 |
|---|---|---|---|---|
| data/train.csv | 22,500 | 22 | 是（subscribe） | 2.70 MB |
| data/test.csv | 7,500 | 21 | 否 | 0.88 MB |

- id 无重复（train: 1~22500），train/test 按 75%/25% 划分；
- 两个文件**均无空单元格（NaN=0）**；分类缺失以字符串 `unknown` 表示；
- 目标分布：no=19,548、yes=2,952，正例率 **13.12%**（不平衡二分类）。

### 5.2 真实数据画像（2026-09-19 实测，洞察报告的事实依据）

**分类字段 unknown 占比**：default 21.60%（最高）、education 4.42%、loan 3.95%、housing 3.94%、marital 1.42%、job 1.22%；contact/month/day_of_week/poutcome 无 unknown。

**pdays 哨兵值**：`pdays=999`（从未联系）仅占 **1.16%**，pdays 范围 0~1048。与经典公开版本（96% 为 999）差异显著，说明天池版本对该字段做过填充加工，需派生"是否曾被联系"特征。

**认购率业务差异**：

- 月份：dec 51.8%、sep 48.9%、mar 50.5%、oct 46.0% 远高于 may 7.0%、jul 10.3%；
- 上次结果 poutcome：success 19.9% > failure 15.0% > nonexistent 11.0%；
- 职业：student 33.0%、retired 27.0% 最高，blue-collar 7.6%、services 9.6% 最低；
- 联系方式：cellular 16.2% 约为 telephone 7.9% 的 2 倍；
- 触达次数：联系 ≥6 次客户占 11.08%，高频触达转化率走低。

**数值特征与标签相关性（皮尔逊系数，Top）**：emp_var_rate -0.270、lending_rate3m -0.181、campaign +0.164、pdays -0.099、age +0.094、nr_employed -0.082。

**duration 口径告警**：通话时长在业务上属"通话结束后才可知"的事后特征，直接用于预测构成数据泄露；且本数据该字段数值整体偏大（认购客户均值约 1283、未认购约 1126），单位口径存疑，建模前必须与业务方核对并原则上剔除。

### 5.3 逻辑数据库模型（本期不落库，为 M2/M3 预留）

本期存储介质为 CSV。为保证后续平滑迁移到关系型数据库，定义如下逻辑模型，字段类型即建库 DDL 依据。

**事实表 `fact_telemarketing_contact`（电话营销触达事实，粒度：一次客户-活动记录）**

| 列名 | 逻辑类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PK | 客户记录唯一标识 |
| age | INTEGER | NOT NULL, CHECK(age BETWEEN 17 AND 100) | 年龄 |
| job | VARCHAR(20) | NOT NULL | 职业，unknown 允许 |
| marital | VARCHAR(10) | NOT NULL | 婚姻状况 |
| education | VARCHAR(30) | NOT NULL | 受教育程度 |
| default | VARCHAR(10) | NOT NULL | 违约记录 |
| housing | VARCHAR(10) | NOT NULL | 住房贷款 |
| loan | VARCHAR(10) | NOT NULL | 个人贷款 |
| contact | VARCHAR(10) | NOT NULL | 联系方式 |
| month | VARCHAR(3) | NOT NULL, CHECK in jan..dec | 最后联系月份 |
| day_of_week | VARCHAR(3) | NOT NULL, CHECK in mon..fri | 最后联系星期 |
| duration | INTEGER | NOT NULL | 通话时长（口径待核；建模特征隔离） |
| campaign | INTEGER | NOT NULL, CHECK(campaign >= 1) | 本次联系次数 |
| pdays | INTEGER | NOT NULL, 999 为哨兵 | 距上次联系天数 |
| previous | INTEGER | NOT NULL, CHECK(previous >= 0) | 历史联系次数 |
| poutcome | VARCHAR(12) | NOT NULL | 上次营销结果 |
| emp_var_rate | DECIMAL(5,2) | NOT NULL | 就业变动率 |
| cons_price_index | DECIMAL(6,2) | NOT NULL | 消费者价格指数 |
| cons_conf_index | DECIMAL(6,2) | NOT NULL | 消费者信心指数 |
| lending_rate3m | DECIMAL(5,2) | NOT NULL | 三个月拆借利率 |
| nr_employed | DECIMAL(7,2) | NOT NULL | 就业人数（千） |
| subscribe | CHAR(2) | NULL, CHECK in ('yes','no') | 目标列；测试集/未来待预测客户为 NULL |

**派生特征（M2 规划，逻辑视图 `v_model_features`）**：`is_ever_contacted`（pdays=999 → 0）、`is_high_frequency`（campaign≥6）、month/contact 等 OneHot 编码、宏观指标标准化列；`duration` 进入隔离视图 `v_leakage_features`，默认不供模使用。

### 5.4 字段映射表（CSV → 代码 schema → DataFrame dtype → 逻辑数据库列）

| CSV 列名 | schema 常量归属 | pandas dtype | DB 列 | 中文名 |
|---|---|---|---|---|
| id | ID_COLUMN | int64 | id INTEGER PK | 客户编号 |
| age | NUMERIC_COLUMNS | int64 | age INTEGER | 年龄 |
| job | CATEGORICAL_COLUMNS | object/string | job VARCHAR(20) | 职业 |
| marital | CATEGORICAL_COLUMNS | string | marital VARCHAR(10) | 婚姻状况 |
| education | CATEGORICAL_COLUMNS(有序) | string | education VARCHAR(30) | 受教育程度 |
| default | BINARY_LIKE_COLUMNS | string | default VARCHAR(10) | 是否违约 |
| housing | BINARY_LIKE_COLUMNS | string | housing VARCHAR(10) | 住房贷款 |
| loan | BINARY_LIKE_COLUMNS | string | loan VARCHAR(10) | 个人贷款 |
| contact | CATEGORICAL_COLUMNS | string | contact VARCHAR(10) | 联系方式 |
| month | CATEGORICAL_COLUMNS(有序) | string | month VARCHAR(3) | 最后联系月份 |
| day_of_week | CATEGORICAL_COLUMNS(有序) | string | day_of_week VARCHAR(3) | 最后联系星期 |
| duration | NUMERIC_COLUMNS | int64 | duration INTEGER | 通话时长（泄露隔离） |
| campaign | NUMERIC_COLUMNS | int64 | campaign INTEGER | 本次联系次数 |
| pdays | NUMERIC_COLUMNS | int64（999 哨兵） | pdays INTEGER | 距上次联系天数 |
| previous | NUMERIC_COLUMNS | int64 | previous INTEGER | 历史联系次数 |
| poutcome | CATEGORICAL_COLUMNS | string | poutcome VARCHAR(12) | 上次营销结果 |
| emp_var_rate | NUMERIC_COLUMNS | float64 | emp_var_rate DECIMAL(5,2) | 就业变动率 |
| cons_price_index | NUMERIC_COLUMNS | float64 | cons_price_index DECIMAL(6,2) | 消费者价格指数 |
| cons_conf_index | NUMERIC_COLUMNS | float64 | cons_conf_index DECIMAL(6,2) | 消费者信心指数 |
| lending_rate3m | NUMERIC_COLUMNS | float64 | lending_rate3m DECIMAL(5,2) | 三个月拆借利率 |
| nr_employed | NUMERIC_COLUMNS | float64 | nr_employed DECIMAL(7,2) | 就业人数 |
| subscribe | TARGET_COLUMN | string（yes/no） | subscribe CHAR(2) NULL | 是否认购 |

映射实现位置：[schema.py](../src/core/data_explorer/schema.py)（唯一字段事实来源）、[loader.py](../src/core/data_explorer/loader.py)（类型校正）。

---

## 第 6 章 系统架构与模块设计

### 6.1 分层架构

```
用户浏览器
   │  HTTP（Streamlit 脚本驱动）
   ▼
src/frontend/dashboard/app.py        交互层：仅收集控件输入、渲染图表与报告
   │  调用（面向接口，不写业务规则）
   ▼
src/core/data_explorer/              业务层：无 Streamlit 依赖，可独立测试
   ├── interfaces.py                 契约：IDataLoader/IDataFilter/IChartFactory/
   │                                      IInsightGenerator/IDashboardApp + 数据类
   ├── schema.py                     字段字典（唯一事实来源）
   ├── loader.py                     CSV 加载、列校验、类型校正、元信息
   ├── filters.py                    全字段动态筛选
   ├── charts.py                     Plotly 图表工厂（7 类图）
   └── insights.py                   特征洞察报告生成
   │
   ▼
src/utils/logger.py                  基础层：rich 中文彩色日志
   │
   ▼
data/train.csv、data/test.csv        数据层（本期 CSV；M3 替换为 DB 不影响上层）
```

### 6.2 目录结构（遵循 standards/02-PROJECT-STRUCTURE）

```
banksys/
├── data/                              # 原始 CSV（随仓库提交，保证开箱即用）
├── docs/                              # PRD、状态、决策日志
├── src/
│   ├── utils/logger.py
│   ├── core/data_explorer/
│   └── frontend/dashboard/app.py
├── tests/                             # 28 个测试，合成数据夹具
├── .github/workflows/banksys-ci.yml   # 推送时部署到仓库根 .github/workflows/
├── standards/                         # 只读规范（lint/format 已排除）
├── envbank/                           # 本地 venv（gitignore，不提交）
├── pyproject.toml / requirements*.txt / .gitignore / .gitattributes
```

### 6.3 关键设计决策

- **接口先行**：前端只依赖 [interfaces.py](../src/core/data_explorer/interfaces.py) 抽象，M2 增加 DB 加载器时只需新增实现类；
- **前后端解耦**：核心层不 import streamlit，所有业务逻辑可被 pytest 直接验证；
- **缓存策略**：加载器实例内缓存 DataFrame，Streamlit 侧 `@st.cache_resource`/`@st.cache_data` 双层缓存，避免重复读盘。

---

## 第 7 章 模块接口设计

接口完整定义见 [interfaces.py](../src/core/data_explorer/interfaces.py)，契约摘要：

| 接口/数据类 | 关键方法/字段 | 输入 → 输出 | 失败契约 |
|---|---|---|---|
| `IDataLoader` | `load(dataset)` | DatasetName/str → DataFrame | 文件缺失/字段不符抛 `DataLoadingError`（中文） |
| | `describe(dataset)` | → DatasetMeta（行数/认购数/认购率） | 同上 |
| `IDataFilter` | `apply(data, criteria)` | DataFrame + FilterCriteria → 过滤副本 | 引用不存在字段抛 `DataExplorerError` |
| | `default_criteria / categorical_options / numeric_bounds` | 生成默认条件与控件取值域 | — |
| `IChartFactory` | 7 个图表方法 | DataFrame(+列名) → plotly Figure | 无标签调用认购类图表抛 DataExplorerError；空数据返回"无样本"提示图 |
| `IInsightGenerator` | `generate(data, dataset_name)` | → InsightReport（条目含标题/分级/分类/说明/量化证据，可 `to_dict()` 导出） | 空数据返回"请放宽筛选"提示条目 |
| `IDashboardApp` | `render()` | Streamlit 运行时上下文 → 页面 | 筛选异常以 st.error 展示中文原因 |
| `FilterCriteria` | categorical_selections / numeric_ranges | dict 字段→选中值；空列表/None 表示不限制 | — |
| `InsightItem` | title/category/level/content/metrics | level: info/suggest/warn；category: business/quality/feature/modeling | — |

**统一异常层次**：`DataExplorerError`（基类）→ `DataLoadingError`；所有异常消息面向最终用户，必须为简体中文。

**本地调用示例**：

```python
from src.core.data_explorer import CsvDataLoader, DataFilter, PlotlyChartFactory
from src.core.data_explorer.insights import InsightGenerator

loader = CsvDataLoader()
data = loader.load("train")
criteria = DataFilter().default_criteria(data)
filtered = DataFilter().apply(data, criteria)
figure = PlotlyChartFactory().target_distribution(filtered)
report = InsightGenerator().generate(filtered)
```

---

## 第 8 章 验收标准

### 8.1 功能验收（逐条对照第 3 章）

- AC-01：侧边栏可见 train/test 切换；切到 test 后"认购率分组对比"页显示中文警告且不报错；
- AC-02：22 列中 10 个分类多选（train 含 subscribe）+ 11 个数值滑块（含 id）全部可操作；重置按钮生效；
- AC-03：任意筛选后顶部 4 个 KPI 与 5 个页签图表/洞察全部联动刷新；筛选为空时显示"无样本"提示；
- AC-04：字段分布页分类出柱图、数值出直方图，勾选分组后按认购/未认购着色；
- AC-05：热图含 subscribe_编码 维度，系数在 -1~1；
- AC-06：分类认购率图悬停显示样本量；数值分箱档数可调（3~10）；
- AC-07：训练集默认生成 ≥8 条洞察（实测 10 条），含 duration 泄露风险条目与 pdays 质量条目；JSON 可下载；
- AC-08：终端运行全程可见 rich 中文彩色日志。

### 8.2 工程验收（三步自检，定义见状态文档第 4 节）

| 步骤 | 命令 | 通过标准 | 实测 |
|---|---|---|---|
| 静态检查 | `black --check .` + `ruff check .` | 0 违规 | 通过 |
| 单元测试 | `pytest tests/ --cov=src` | 全部通过，覆盖率 ≥80% | 28 passed，92% |
| 无头冒烟 | streamlit AppTest 加载 train、切换 test | 无异常、5 页签齐全、控件齐全 | 通过 |

### 8.3 CI 验收

推送到 main（或 PR）且变更命中 `banksys/**` 时，GitHub Actions `banksys-CI` 工作流全绿；只做 CI，不配置任何 CD 步骤。

---

## 第 9 章 里程碑与项目状态

| 里程碑 | 内容 | 状态（2026-09-19） |
|---|---|---|
| M1 | 交互式数据探索仪表盘 + CI | 开发完成，待用户验收 |
| M2 | 特征工程、模型训练与评估（含 duration 隔离） | 未启动 |
| M3 | 在线预测 API / 批量预测 | 未启动 |
| M4 | CD/容器化部署（按需） | 未启动 |

详细进度、已完成/进行中模块见 [PROJECT-STATUS-v2.0.md](PROJECT-STATUS-v2.0.md)；所有关键取舍见 [PROJECT-DECISION-LOG-v2.0.md](PROJECT-DECISION-LOG-v2.0.md)。

---

## 第 10 章 风险、假设与依赖

### 10.1 风险与应对

| 风险 | 等级 | 说明 | 应对 |
|---|---|---|---|
| duration 数据泄露 | 高 | 事后特征，若带入模型将导致线下虚高、上线失效 | 洞察报告红色风险提示；M2 默认剔除并隔离视图 |
| duration 单位口径不明 | 中 | 数值整体偏大（均值约 1146） | 已在数据字典与洞察标注，建模前与业务方核对 |
| default 高 unknown（21.6%） | 中 | 直接当类别可能引入噪声 | 作为独立类别保留；M2 对比 WOE/插补方案 |
| 类别不平衡（13.12%） | 中 | 准确率指标失效 | M2 采用 PR-AUC、召回率、Lift/增益曲线评估 |
| 数据随仓库提交 | 低 | 体积约 3.6 MB，可接受；更大数据需改方案 | 决策 DEC-005：本期提交，后续迁 Git LFS/对象存储 |
| 规范版本不一致 | 中 | 任务引用的 v2.0 规范文件缺失 | DEC-001：以现有 00-09 系列为准并显式记录 |

### 10.2 假设

1. CSV 编码 UTF-8、逗号分隔、首行表头（已验证可正常读取）；
2. 数据为脱敏统计字段，可在教学项目仓库内提交；
3. 本地运行环境为 Windows + Python 3.10，CI 为 Ubuntu + Python 3.10；
4. 月份/星期等缩写语义与经典数据集一致（month: aug=八月等）。

### 10.3 依赖

- 运行时：streamlit>=1.36、pandas>=2.0、plotly>=5.20、rich>=13.7；
- 开发：pytest>=8、pytest-cov>=5、black>=24、ruff>=0.5；
- 外部：GitHub Actions（CI）；无数据库、无外部 API 依赖。
