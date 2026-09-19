# 知识索引 KNOWLEDGE-INDEX-v2.0 —— banksys

> 本文件是 banksys 项目的知识入口：数据 schema 摘要、模块地图、常用命令、规范与决策索引。
> 版本：v2.0 | 最后更新：2026-09-19（M2 模型训练完成）

---

## 1. 项目一句话说明

基于银行电话营销历史数据（天池数据集，约 3 万样本），预测客户是否认购定期存款，
当前已完成 M1 交互式数据探索仪表盘与 M2 多模型训练，后续 M3 为在线预测服务。

- 仓库：`https://github.com/leequer/CICDTEST`（多应用仓库，本应用位于 `banksys/`）
- 语言/环境：Python 3.10；统一虚拟环境 `banksys/envbank`（venv，无 conda 时的授权替代，DEC-002）
- 规范基线：standards/ 目录 00-09 系列（v2.0 规范文件不存在，DEC-001）

---

## 2. 数据 Schema 摘要（唯一事实来源：src/core/data_explorer/schema.py）

### 2.1 数据集

| 数据集 | 文件 | 行数 | 列数 | 目标列 |
|---|---|---|---|---|
| 训练集 | data/train.csv | 22,500 | 22 | subscribe（no 19,548 / yes 2,952，正例率 13.12%） |
| 测试集 | data/test.csv | 7,500 | 21 | 无标签，仅供预测 |

无 NaN；缺失语义以字符串 `unknown` 表示；`id` 1-22500 无重复。

### 2.2 字段（22 列）

- 标识：`id`（不入模）
- 目标：`subscribe`（yes/no → 1/0）
- 分类字段（10 个，OneHot 编码）：
  `job, marital, education, default, housing, loan, contact, month, day_of_week, poutcome`
- 数值字段（10 个，StandardScaler 标准化）：
  `age, duration, campaign, pdays, previous, emp_var_rate, cons_price_index, cons_conf_index, lending_rate3m, nr_employed`
- 哨兵值：`pdays=999` 表示从未联系（占 1.16%，天池改版口径）
- 泄露红线：`duration` 为通话结束后才可知的事后特征，M2 默认隔离（DEC-008），
  对照实验证明纳入后 PR-AUC 反降 0.01

### 2.3 M2 建模特征（24 个入模）

- 衍生特征（5 个，src/core/model_training/features.py）：
  - `is_ever_contacted`：pdays≠999（二值）
  - `is_high_frequency`：campaign≥6（二值）
  - `was_previous_success`：poutcome=success（二值）
  - `contact_cellular`：contact=cellular（二值）
  - `age_bucket`：年龄分箱（分类，4 段）
- 入模清单：11 分类（10 原始 + age_bucket）+ 13 数值（9 原始 + 4 二值，duration 已剔除）
- 完整字段血缘：`db/field_mapping.json`（训练时自动生成）

---

## 3. 模块地图

| 层 | 路径 | 职责 |
|---|---|---|
| 字段字典 | src/core/data_explorer/schema.py | 全项目唯一字段事实来源 |
| M1 数据探索 | src/core/data_explorer/（loader/filters/charts/insights/interfaces） | 加载、筛选、Plotly 图表、特征洞察 |
| M1 仪表盘 | src/frontend/dashboard/app.py | Streamlit 5 页签交互仪表盘（8501） |
| M2 训练配置 | src/core/model_training/config.py | 随机种子、切分比例、阈值、收益假设、路径 |
| M2 特征工程 | src/core/model_training/features.py | 衍生特征 + db/field_mapping.json |
| M2 预处理 | src/core/model_training/preprocessing.py | 目标编码、分层切分、OneHot+标准化、三段式流水线 |
| M2 模型 | src/core/model_training/models.py | LR / RandomForest / XGBoost / LightGBM 工厂与网格 |
| M2 调优 | src/core/model_training/tuning.py | GridSearchCV（3 折，主指标 PR-AUC） |
| M2 评估 | src/core/model_training/evaluation.py | ROC-AUC、PR-AUC、F1 最优阈值、混淆矩阵 |
| M2 收益 | src/core/model_training/benefit.py | 外呼成本/认购收益模拟、阈值扫描 |
| M2 编排 | src/core/model_training/pipeline.py | 全链路编排、选模型、产物落盘 |
| M2 入口 | src/core/model_training/train.py | `python -m src.core.model_training.train` |
| 公共日志 | src/utils/logger.py | rich + 简体中文 + 六级颜色（含自定义 SUCCESS） |

产物目录：

- `models/best_model.joblib`：最佳模型三段式流水线（gitignore，重新训练生成）
- `models/training_report.json`：四模型指标、最佳参数、收益阈值表（入库）
- `models/duration_leakage_comparison.json`：duration 泄露对照证据（入库）
- `db/field_mapping.json`：字段映射与血缘（入库）

---

## 4. M2 模型成绩（2026-09-19，测试集 4,500 行）

| 模型 | CV PR-AUC | 测试 ROC-AUC | 测试 PR-AUC | F1 | 推荐阈值外呼净收益 |
|---|---|---|---|---|---|
| LogisticRegression | 0.3875 | 0.8104 | 0.4473 | 0.5316 | 29,480 |
| RandomForest | 0.4452 | 0.8205 | 0.5025 | 0.5599 | 30,970 |
| **XGBoost（入选）** | 0.4372 | 0.8168 | **0.5080** | 0.5468 | 29,240 |
| LightGBM | 0.4278 | 0.8100 | 0.5023 | 0.5530 | 30,220 |

业务结论（占位口径：每通电话 10 元、每笔认购收益 100 元，待业务校准）：
阈值 0.5 时只外呼 22.1% 客户即可捕获 70.2% 认购者，模拟净收益 31,460 元，
比全员外呼基线（14,000 元）提升 17,460 元（+124.7%）。

---

## 5. 常用命令（PowerShell，在 banksys/ 目录）

```powershell
.\envbank\Scripts\Activate.ps1

# M1 仪表盘
streamlit run src/frontend/dashboard/app.py

# M2 训练（全量网格调优 + duration 对照，约 4-6 分钟）
python -m src.core.model_training.train --compare-duration
# 快速冒烟（不调参）
python -m src.core.model_training.train --quick --only logistic_regression

# 四道门禁（CI 同款）
black --check .
ruff check .
mypy src
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80
```

---

## 6. 规范与决策索引

- 规范：standards/00-QUICK-START.md、01-CICD-SETUP-GUIDE.md、02-PROJECT-STRUCTURE.md、
  04-GITHUB-ACTIONS-TEMPLATE.md、05-LESSONS-LEARNED.md、08-CODE-STYLE.md
- 产品需求：docs/PRD-v2.0.md（10 章节，含逻辑数据库模型与字段映射表）
- 项目状态：docs/PROJECT-STATUS-v2.0.md
- 决策记录：docs/PROJECT-DECISION-LOG-v2.0.md（DEC-001 起）
- CI：.github/workflows/banksys-ci.yml（Black → Ruff → MyPy → pytest 覆盖率 80%，只 CI 不 CD）

## 7. 环境与网络备忘

- git 访问 GitHub：本地代理 127.0.0.1:31181 + `-c http.version=HTTP/1.1`（DEC-013）
- PowerShell 5.1 给原生命令传参会吞双引号：内联 Python 用单引号或临时脚本文件
- 依赖安装只允许进入 envbank，禁止污染系统 Python
