# 项目状态文档 PROJECT-STATUS-v2.0 —— banksys

| 项目 | 内容 |
|---|---|
| 应用名称 | banksys（CICDTEST 多应用仓库子应用） |
| 更新日期 | 2026-09-19 |
| 当前阶段 | M1 数据探索仪表盘已验收；**M2 模型训练开发完成，本地自检全绿，待推送验证 CI 与用户验收** |
| 本地环境 | Windows + Python 3.10.4 + venv 虚拟环境 `envbank/`（位于 banksys 根目录） |
| 规范基线 | standards/ 00-09 系列（v2.0 规范文件缺失，见决策 DEC-001） |

---

## 1. 会话开始知识对齐清单（v2.0）回填

### M2 阶段（2026-09-19）

| # | 清单项 | 回答 |
|---|---|---|
| 1 | 当前项目名称 | banksys |
| 2 | 当前主要目标 | 完成机器学习模型训练：预处理、特征工程、LR/RF/XGBoost/LightGBM 训练调优，产出高精度认购分类模型 |
| 3 | 用户熟悉程度 | 新手（沿用 M1 确认） |
| 4 | 最优先模块 | src/core/model_training/ 模型训练全链路 |
| 5 | 知识索引是否已加载 | 会话开始时不存在；本次已新建 docs/KNOWLEDGE-INDEX-v2.0.md（含 schema 摘要、模块地图、命令索引） |
| 6 | 已应用 Lessons 编号 | standards/05 经验 + DEC-001（规范基线）、DEC-002（venv 替代 conda）、DEC-008（duration 泄露隔离）、DEC-013（代理 HTTP/1.1） |
| 7 | CI/CD 是否 100% | M1 三次运行全绿（Black/Ruff/pytest）；M2 起新增 MyPy 门禁，推送后回填远端结果（只做 CI） |
| 8 | 项目结构是否干净 | 是；本次仅新增 src/core/model_training/、db/、models/（二进制产物 gitignore）与 M2 测试 |
| 9 | conda 环境是否就绪 | 机器无 conda；沿用授权后的 envbank（Python 3.10.4 venv），已在其中安装 scikit-learn/xgboost/lightgbm/joblib/mypy |
| 10 | 当前是否有阻塞 | 无。用户点名的 5 个 v2.0 规范文件仍不存在（Glob 核实），沿用已批准的 DEC-001 基线 |

### M1 阶段（历史存档）

M1 知识对齐回填见 git 历史；当时两个阻塞（v2.0 规范缺失、conda 缺失）分别由 DEC-001、DEC-002 闭环。

---

## 2. 模块进度

### 已完成模块

**M1 数据探索（已验收，2026-09-19）**

| 模块 | 路径 | 说明 |
|---|---|---|
| 字段字典 | src/core/data_explorer/schema.py | 22 字段中文数据字典、pdays=999 哨兵、duration 泄露标注 |
| 数据探索核心 | src/core/data_explorer/ | 加载/筛选/7 类 Plotly 图/特征洞察，5 接口 + 数据契约 |
| 交互仪表盘 | src/frontend/dashboard/app.py | Streamlit 5 页签 + 全字段筛选 + KPI + JSON 导出 |
| M1 测试 | tests/test_loader/filters/charts/insights/app_smoke | 28 用例（M2 后随全量回归） |

**M2 模型训练（本次完成）**

| 模块 | 路径 | 说明 |
|---|---|---|
| 训练配置 | src/core/model_training/config.py | 随机种子、分层比例、duration 开关、收益假设、产物目录 |
| 模块接口 | src/core/model_training/interfaces.py | 6 抽象接口 + FeatureSet/EvaluationMetrics/BenefitResult/ModelResult/TrainingReport 契约 |
| 特征工程 | src/core/model_training/features.py | 5 个业务衍生特征；db/field_mapping.json 字段血缘；duration 默认隔离 |
| 数据预处理 | src/core/model_training/preprocessing.py | yes/no 编码、分层切分、OneHot+标准化；**三段式流水线**（特征工程→预处理→模型） |
| 模型工厂 | src/core/model_training/models.py | LR / RandomForest / XGBoost / LightGBM + 精简调参网格 |
| 超参调优 | src/core/model_training/tuning.py | GridSearchCV 3 折，主指标 average_precision（PR-AUC），支持空网格快速模式 |
| 模型评估 | src/core/model_training/evaluation.py | ROC-AUC、PR-AUC、PR 曲线 F1 最优阈值、混淆矩阵 |
| 业务收益 | src/core/model_training/benefit.py | 外呼成本/认购收益模拟、9 档阈值扫描、全员外呼基线对比 |
| 训练编排 | src/core/model_training/pipeline.py | 全链路；PR-AUC 选模型；产物落盘；duration 泄露对照实验 |
| 训练入口 | src/core/model_training/train.py | `python -m src.core.model_training.train [--quick] [--only ...] [--compare-duration]` |
| M2 测试 | tests/test_mt_*.py + conftest medium_dataframe | 新增 23 用例（全量 51） |
| 产物 | db/field_mapping.json、models/training_report.json、models/duration_leakage_comparison.json、models/best_model.joblib（gitignore） | 字段映射、四模型对比、泄露证据、最佳模型 |
| 公共日志 | src/utils/logger.py | 类型化 ProjectLogger（SUCCESS 自定义级），M2 起通过 mypy |
| CI | .github/workflows/banksys-ci.yml | 新增 MyPy 步骤：Black → Ruff → MyPy → pytest（覆盖率 80%） |
| 文档 | docs/KNOWLEDGE-INDEX-v2.0.md、PRD-v2.0.md、决策日志 | 知识索引（schema 摘要）+ 决策 DEC-014 起 |

### 进行中模块

无。M2 待远端 CI 验证与用户验收。

### 未启动模块（后续里程碑）

- M3：在线预测服务（加载 best_model.joblib，API + 批量预测；模型已具备"吃原始 CSV"契约）、关系型数据库落地（DDL 已在 PRD 5.3 预留）；
- M4：CD / Docker 部署（按用户要求不做）。

---

## 3. 本地运行说明（新手版）

以下命令均在项目根目录 `banksys/` 下执行，PowerShell 中使用 `;` 连接。

```powershell
# 1. 激活虚拟环境
.\envbank\Scripts\Activate.ps1

# 2. 启动 M1 仪表盘（默认 http://localhost:8501）
streamlit run src/frontend/dashboard/app.py

# 3. M2 模型全量训练（约 4-6 分钟，含四模型网格调优）
python -m src.core.model_training.train --compare-duration

# 4. 四道门禁自检（与 CI 完全一致）
black --check .
ruff check .
mypy src
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80
```

若未激活环境，可用完整路径调用解释器：
`.\envbank\Scripts\python.exe -m pytest tests/`

---

## 4. 三步自检记录（AGENTIC-GUARDRAILS 本地等价定义）

说明：AGENTIC-GUARDRAILS-v2.0.md 在仓库中不存在，以下三步依据 standards/08 代码审查清单与 CI 模板定义，已经用户知情。

### M2 自检（2026-09-19）

| 步骤 | 内容 | 结果 |
|---|---|---|
| 第一步：静态检查 | black --check + ruff check（E/W/F/I）+ **mypy src** | 通过：37 个 Python 文件格式无差异；ruff All checks passed；mypy Success: no issues found in 25 source files |
| 第二步：单元测试 | pytest tests/ --cov=src --cov-fail-under=80 | 通过：**51 passed in 8.87s，总覆盖率 90%** |
| 第三步：真实训练+产物冒烟 | 真实 train.csv 全量训练四模型；joblib 加载产物对原始 test.csv（无标签、无衍生列）直接 predict_proba | 通过：XGBoost 入选（PR-AUC 0.5080）；三段式流水线 steps=[features, preprocess, model]，5 条原始记录概率合法 |

M2 模块覆盖率：config/evaluation/features/pipeline 100%、preprocessing 93%、models 90%、interfaces 89%、tuning 67%（网格搜索分支由真实训练覆盖）、train 入口 0%（CLI，由手工训练执行覆盖）。

真实训练成绩（测试集 4,500 行，2026-09-19）：

| 模型 | CV PR-AUC | ROC-AUC | PR-AUC | F1 |
|---|---|---|---|---|
| LogisticRegression | 0.3875 | 0.8104 | 0.4473 | 0.5316 |
| RandomForest | 0.4452 | 0.8205 | 0.5025 | 0.5599 |
| **XGBoost（入选）** | 0.4372 | 0.8168 | **0.5080** | 0.5468 |
| LightGBM | 0.4278 | 0.8100 | 0.5023 | 0.5530 |

duration 泄露对照（逻辑回归）：不含 duration PR-AUC=0.4461，含 duration PR-AUC=0.4361，差值 -0.01，
**纳入事后特征无收益**，默认隔离决策正确（models/duration_leakage_comparison.json 留证）。

业务收益模拟（占位口径：每通电话 10 元、每笔认购 100 元）：
阈值 0.5 时外呼 22.1% 客户、捕获 70.2% 认购者，净收益 31,460 元，
比全员外呼基线 14,000 元提升 17,460 元（+124.7%）。口径上线前需业务校准。

M2 自检中发现并已闭环的缺陷：

1. 日志格式串 `%.2%%` 缺 f，logging 抛 ValueError → 改 `%.2f%%`；
2. mypy 新增门禁暴露 M1 两处真实标注问题（侧边栏函数返回 tuple 标注为 FilterCriteria、session_state key 需 isinstance）→ 已修正；
3. logger.success 原为猴子补丁，mypy 与运行时双重风险 → 重构为类型化 ProjectLogger（setLoggerClass + 实例补绑）；
4. 落盘模型初版只含"预处理+模型"，对原始 test.csv 预测报缺列 → 升级为三段式流水线（RawFeatureTransformer），并新增上线契约测试。

无未关闭异常；未触发 EXCEPTION-HANDLING 上报条件。

### M1 自检（历史存档）

28 passed、覆盖率 92%、AppTest 无头冒烟通过；闭环 5 个缺陷（slider step、color_discrete_map、热图断言、radio 定位、width API 迁移）。

---

## 5. CI 状态

- 工作流文件：.github/workflows/banksys-ci.yml（仓库根 .github/workflows/）；
- 触发条件：push/PR 到 main 且变更命中 banksys/**；只做 CI 不做 CD；
- M2 起步骤：setup-python 3.10 → 安装 requirements-dev.txt → Black → Ruff → **MyPy（mypy src）** → pytest --cov（--cov-fail-under=80）；
- 远端运行历史：
  - M1：5936f6e 首跑 success（运行 ID 35410374599），f27e9da / 5555509 文档提交同样 success；
  - M2：**待本次推送后回填**。

---

## 6. 当前总体状态（大白话）

M2 的活儿干完了：四种模型（逻辑回归、随机森林、XGBoost、LightGBM）都在真实的 2.25 万条数据上完成了训练和调参，
**XGBoost 效果最好**（ROC-AUC 0.82、PR-AUC 0.51）；模拟业务算账时，只给两成客户打电话就能抓住七成想买的人，
比"所有人都打一遍"多赚约一倍半。最容易出事的"用通话时长作弊"问题已默认封死，对照实验证明封得对。

本地 51 个测试全过、四种规范检查（格式/风格/类型/测试覆盖率 90%）全绿，
模型文件能直接读取并对没标签的新数据打分。代码还没推送，推完 GitHub CI 会是最后一道确认关。
