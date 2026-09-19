# 项目决策日志 PROJECT-DECISION-LOG-v2.0 —— banksys

> 规则：每个重要取舍一条记录，包含背景、决策、理由、影响；只追加、不改写历史。

| 决策编号 | 日期 | 主题 | 状态 |
|---|---|---|---|
| DEC-001 | 2026-09-19 | v2.0 规范文件缺失时的规范基线 | 已确认 |
| DEC-002 | 2026-09-19 | conda 缺失，改用 venv 创建 envbank | 已确认 |
| DEC-003 | 2026-09-19 | Python 版本基线 3.10 | 已确认 |
| DEC-004 | 2026-09-19 | 包管理工具采用 pip 而非 uv | 已确认 |
| DEC-005 | 2026-09-19 | 数据 CSV 随仓库提交 | 已确认 |
| DEC-006 | 2026-09-19 | 只做 CI、不做 CD，多应用仓库隔离 | 已确认 |
| DEC-007 | 2026-09-19 | unknown 作为独立类别保留 | 已确认 |
| DEC-008 | 2026-09-19 | duration 列为数据泄露高风险特征 | 已确认 |
| DEC-009 | 2026-09-19 | 小样本分组结论阈值 30 | 已确认 |
| DEC-010 | 2026-09-19 | Streamlit 宽度 API 迁移 width="stretch" | 已确认 |
| DEC-011 | 2026-09-19 | 测试集无标签，认购类分析显式禁用 | 已确认 |
| DEC-012 | 2026-09-19 | CI 覆盖率门槛设为 80% | 已确认 |

---

## DEC-001 v2.0 规范文件缺失时的规范基线

- **背景**：任务要求严格遵循 standards/ 下 DEVELOPMENT-NORM-v2.0.md、PROJECT-STRUCTURE-v2.0.md、PRD-MANAGEMENT-v2.0.md、CODE-STYLE-v2.0.md、AGENTIC-GUARDRAILS-v2.0.md、EXCEPTION-HANDLING-v2.0.md、MODULE-INTERFACE-STANDARD-v2.0.md、KNOWLEDGE-INDEX-v2.0.md 等文件。实际勘察确认这些文件**均不存在**，目录内只有 00-09 系列（INDEX 自标注 v3.0）。
- **决策**：经用户确认（AskUserQuestion，2026-09-19），以 standards/ 实际存在的 00-09 系列（重点 02 项目结构、08 代码风格、04/01 CI 模板、05 Lessons）为执行基线；PRD/状态/决策日志按任务要求的 v2.0 命名与 10 章节结构编写，并在文档显著位置标注依据。
- **理由**：不能伪造不存在的规范文本再假装合规；现有规范可覆盖结构、风格、CI、跨平台等主要诉求。
- **影响**：若后续补齐真正的 v2.0 规范，需做一次差距分析（Gap Analysis）并按新规范修订；AGENTIC 三步自检采用本地等价定义（见 STATUS 第 4 节）。

## DEC-002 conda 缺失，改用 venv 创建 envbank

- **背景**：用户约定"项目虚拟环境通过 conda 创建，统一虚拟环境为 envbank"。勘察发现 conda 不在 PATH、无 CONDA 环境变量、常见安装目录均无 conda；系统仅有 Python 3.10.4。
- **决策**：经用户授权（"使用python 创建 env"），使用系统 Python 3.10 的 venv 在 `banksys/envbank/` 创建同名虚拟环境。
- **理由**：满足统一环境名与隔离性要求；不擅自安装 Miniconda、不污染系统环境（符合环境问题最小干预原则）。
- **影响**：激活命令为 `.\envbank\Scripts\Activate.ps1` 而非 `conda activate envbank`；若未来安装 conda，需重建环境并重新验证 requirements。

## DEC-003 Python 版本基线 3.10

- **背景**：standards 模板 pyproject 写 requires-python >=3.11，CI 矩阵 3.11/3.12；本机唯一可用解释器为 Python 3.10.4。
- **决策**：项目与 CI 统一 Python 3.10；代码不使用 3.11+ 独有语法。
- **理由**：本地与 CI 环境一致优先；streamlit/pandas/plotly 均完整支持 3.10。
- **影响**：后续如升 3.11+ 只需改 requires-python 与 CI matrix；类型写法采用 `from __future__ import annotations` 保证前向兼容。

## DEC-004 包管理工具采用 pip 而非 uv

- **背景**：08-CODE-STYLE 推荐 `uv run` 工作流；环境内未安装 uv。
- **决策**：统一使用 venv 自带 pip + requirements.txt / requirements-dev.txt，CI 同样使用 pip。
- **理由**：与 DEC-002 的 venv 工具链保持单一事实，避免引入未经验证的新工具。
- **影响**：依赖通过 requirements 文件锁定下限版本；需要可复现锁定时再引入 requirements.lock 或 uv。

## DEC-005 数据 CSV 随仓库提交

- **背景**：train.csv（2.70 MB）与 test.csv（0.88 MB）合计约 3.6 MB；仪表盘本地运行与 AppTest 冒烟都需要 data/ 目录存在。
- **决策**：将 data/*.csv 纳入 git 提交（.gitignore 不排除 data/）。
- **理由**：教学项目、数据已脱敏、体积极小，保证 clone 后开箱即用；单元测试本身用合成数据，不依赖大文件。
- **影响**：数据更新需走 git；若未来数据量显著增大，迁移到 Git LFS 或对象存储并改写加载器路径。

## DEC-006 只做 CI、不做 CD，多应用仓库隔离

- **背景**：CICDTEST 为多应用仓库；用户明确"只做 CI，本地部署即可"。
- **决策**：工作流命名 `banksys-ci.yml`，on.paths 限定 `banksys/**` 与工作流自身，所有步骤 `working-directory: banksys`；不包含任何 SSH/Docker 部署 Job。
- **理由**：避免其他应用变更误触发本应用流水线；满足只 CI 不 CD 的范围约束。
- **影响**：仓库根新增/更新 .github/workflows/banksys-ci.yml；既有工作流不做任何改动。

## DEC-007 unknown 作为独立类别保留

- **背景**：分类字段用字符串 unknown 表示缺失（default 高达 21.60%），并非空值。
- **决策**：加载器把分类列空值填充为 unknown，但不删除样本、不做众数插补；unknown 作为正常类别参与筛选、作图与建模。
- **理由**：unknown 本身可能携带业务信息（如不愿披露违约记录的客群）；删除会改变样本分布。
- **影响**：M2 建模时再对比"独立类别 vs 插补"两种方案的效果。

## DEC-008 duration 列为数据泄露高风险特征

- **背景**：实测 duration 与标签相关系数仅 +0.037，但业务定义为通话结束后才能确定的事后特征；且数值整体偏大（认购/未认购均值约 1283/1126），单位口径存疑。
- **决策**：本期保留用于探索但在数据字典、洞察报告中以"风险提示（红）"显式标注泄露红线；M2 默认从建模特征中剔除，逻辑上隔离到 v_leakage_features。
- **理由**：泄露与否取决于特征在预测时点是否可得，与当前相关系数大小无关。
- **影响**：防止后续阶段直接把 duration 喂入模型造成线下虚高。

## DEC-009 小样本分组结论阈值 30

- **背景**：按分类字段计算各组认购率时，样本极少的组会产生极端比率（如 1 人认购即 100%）。
- **决策**：组样本量 < 30 的分组不参与"最高/最低认购率"业务洞察。
- **理由**：30 是常用最小统计样本量经验值，避免仪表盘用户被偶然值误导。图表仍展示全部组，仅洞察结论受限。
- **影响**：阈值集中在 insights.py `_MIN_SAMPLE_SIZE` 常量，后续可按评审意见调整。

## DEC-010 Streamlit 宽度 API 迁移 width="stretch"

- **背景**：本机安装的 Streamlit 版本提示 `use_container_width` 将于 2025-12-31 后移除（当前日期已晚于该时点）。
- **决策**：全部 plotly_chart/dataframe/button 迁移为 `width="stretch"`；download_button 使用默认宽度。
- **理由**：避免近期版本升级导致页面报错；CI 安装最新 streamlit 同样受益。
- **影响**：要求 streamlit 支持 width 参数（>=1.36 系列新版本满足），已在 requirements 下限中覆盖。

## DEC-011 测试集无标签，认购类分析显式禁用

- **背景**：test.csv 无 subscribe 列。
- **决策**：图表工厂的认购类方法在无标签时抛出 DataExplorerError（中文消息）；仪表盘切换到 test 后自动隐藏/警告相关页签内容，不静默给出错误图形。
- **理由**：显式失败优于错误结果，符合"异常面向用户可读"的约束。
- **影响**：无标签数据仍可使用分布图、热图（不含标签编码）、数据质量与字段字典。

## DEC-012 CI 覆盖率门槛设为 80%

- **背景**：08-CODE-STYLE 规定最低覆盖率 80%、核心业务逻辑 100%。
- **决策**：CI 以 `--cov-fail-under=80` 作为硬门禁；当前总覆盖率 92%，未对 100% 做硬性要求（图表分支与 UI 回调有少量防御性代码）。
- **理由**：先守住统一底线；M2 建模核心逻辑（数据管线/指标计算）再单独追求 100%。
- **影响**：覆盖率下降到 80% 以下时 CI 红灯。
