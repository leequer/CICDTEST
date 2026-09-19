# 项目状态文档 PROJECT-STATUS-v2.0 —— banksys

| 项目 | 内容 |
|---|---|
| 应用名称 | banksys（CICDTEST 多应用仓库子应用） |
| 更新日期 | 2026-09-19 |
| 当前阶段 | M1 数据分析交互性 —— 开发完成，待用户验收 |
| 本地环境 | Windows + Python 3.10.4 + venv 虚拟环境 `envbank/`（位于 banksys 根目录） |
| 规范基线 | standards/ 00-09 系列（v2.0 规范文件缺失，见决策 DEC-001） |

---

## 1. 会话开始知识对齐清单（v2.0）回填

| # | 清单项 | 回答 |
|---|---|---|
| 1 | 当前项目名称 | banksys |
| 2 | 当前主要目标 | 用 Streamlit 构建银行营销数据交互式探索仪表盘（动态筛选/Plotly 可视化/特征洞察） |
| 3 | 用户熟悉程度 | 新手（文档与命令均给出详细说明） |
| 4 | 最优先模块 | 数据分析交互性 |
| 5 | 知识索引是否已加载 | 未加载：KNOWLEDGE-INDEX-v2.0.md 不存在；以 standards/INDEX.md（v3.0）作为导航替代 |
| 6 | 已应用 Lessons 编号 | 引用 standards/05-LESSONS-LEARNED.md 经验：CI 必须安装 dev 依赖、.gitattributes 统一 LF、Token 不当文本输出 |
| 7 | CI/CD 是否 100% | 本次只做 CI、本地部署；banksys-CI 工作流已配置，首次远端运行结果见第 5 节（推送后回填） |
| 8 | 项目结构是否干净 | 是。banksys 仅含 data/、standards/，本次按 02-PROJECT-STRUCTURE 新建 src/tests/docs，无历史垃圾文件 |
| 9 | conda 环境是否就绪 | 机器无 conda（PATH、常见目录、环境变量均不存在）；经用户授权改用 Python 3.10 venv 创建 envbank（DEC-002） |
| 10 | 当前是否有阻塞 | 会话开始时有两个（v2.0 规范缺失、conda 缺失），均已经用户决策闭环；当前无阻塞 |

---

## 2. 模块进度

### 已完成模块（M1 全部范围）

| 模块 | 路径 | 说明 |
|---|---|---|
| 字段字典 | src/core/data_explorer/schema.py | 22 字段中文数据字典、分类/数值/有序字段、pdays=999 哨兵、duration 泄露标注 |
| 模块接口 | src/core/data_explorer/interfaces.py | 5 个抽象接口 + 6 个数据契约 + 中文异常层次 |
| 数据加载 | src/core/data_explorer/loader.py | CSV 加载、列完整性校验、类型校正、缓存、DatasetMeta |
| 动态筛选 | src/core/data_explorer/filters.py | 10 分类多选 + 11 数值区间、业务顺序排列、默认条件、非法字段拦截 |
| 图表工厂 | src/core/data_explorer/charts.py | 7 类 Plotly 图：目标分布、分类/数值分布、分类/数值认购率对比、相关性热图、缺失概览 |
| 特征洞察 | src/core/data_explorer/insights.py | 4 类 3 级洞察、小样本保护（≥30）、量化证据、JSON 序列化；实测 10 条结论 |
| 交互仪表盘 | src/frontend/dashboard/app.py | 5 页签 + 侧边栏全字段筛选 + KPI + 数据集切换 + JSON 导出 |
| 统一日志 | src/utils/logger.py | rich + 简体中文 + 六级规定颜色 |
| 单元测试 | tests/（5 个测试文件，28 个用例） | 加载/筛选/图表/洞察 + Streamlit AppTest 无头冒烟 |
| 工程配置 | pyproject.toml、requirements*.txt、.gitignore、.gitattributes | black/ruff/pytest 配置，LF 换行 |
| CI 工作流 | .github/workflows/banksys-ci.yml | 仅 CI；paths 隔离 banksys；覆盖率门槛 80% |
| 文档 | docs/PRD-v2.0.md、本文档、决策日志 | 10 章节 PRD，含逻辑数据库模型与字段映射表 |

### 进行中模块

无。等待用户验收 M1。

### 未启动模块（后续里程碑）

- M2：特征工程管线（pdays 派生、OneHot、标准化）、模型训练与评估（PR-AUC/Lift）、duration 隔离视图；
- M3：在线预测服务（API + 批量预测）、关系型数据库落地（DDL 已在 PRD 5.3 预留）；
- M4：CD / Docker 部署（按用户要求本期不做）。

---

## 3. 本地运行说明（新手版）

以下命令均在项目根目录 `banksys/` 下执行，PowerShell 中使用 `;` 连接。

```powershell
# 1. 激活虚拟环境（已创建于 banksys/envbank）
.\envbank\Scripts\Activate.ps1

# 2. 启动仪表盘（本地部署，默认 http://localhost:8501）
streamlit run src/frontend/dashboard/app.py

# 3. 运行测试与自检（无需启动服务）
black --check .
ruff check .
pytest tests/ -v --cov=src --cov-report=term-missing
```

若未激活环境，可用完整路径调用解释器：
`.\envbank\Scripts\python.exe -m pytest tests/`

---

## 4. 三步自检记录（AGENTIC-GUARDRAILS 本地等价定义）

说明：AGENTIC-GUARDRAILS-v2.0.md 在仓库中不存在，以下三步依据 standards/08 代码审查清单与 CI 模板定义，已经用户知情。

| 步骤 | 内容 | 执行时间 | 结果 |
|---|---|---|---|
| 第一步：静态检查 | black --check . （格式）+ ruff check . （风格 E/W/F/I） | 2026-09-19 | 通过：21 个文件格式无差异，ruff All checks passed |
| 第二步：单元测试 | pytest tests/ --cov=src | 2026-09-19 | 通过：28 passed in 5.64s，总覆盖率 92%（最低门槛 80%） |
| 第三步：无头冒烟 | streamlit.testing AppTest：train 默认渲染、切换 test | 2026-09-19 | 通过：无异常，5 页签、11 个多选、11 个滑块、KPI 齐全 |

分模块覆盖率：loader 93%、filters 94%、charts 91%、insights 98%、app 91%、schema/logger 100%。

自检中发现并已闭环的缺陷（均已修复并复测通过）：

1. slider 的 step 为 int 而边界为 float，Streamlit 报类型错误 → 统一 float；
2. Plotly 分组图误用 color_discrete_map 传列表 → 改为中文键映射字典；
3. 热图断言取值位置随 Plotly 版本变化 → 改断言 data[0].x；
4. AppTest 侧边栏 radio 定位假设错误 → 按 label 定位；
5. Streamlit 新版废弃 use_container_width → 迁移 width="stretch"。

无未关闭异常；未触发 EXCEPTION-HANDLING 上报条件。

---

## 5. CI 状态

- 工作流文件：.github/workflows/banksys-ci.yml（推送到 CICDTEST 后位于仓库根 .github/workflows/）；
- 触发条件：push/PR 到 main 且变更命中 banksys/**；
- 步骤：setup-python 3.10 → pip 安装 requirements-dev.txt → black --check → ruff check → pytest --cov（--cov-fail-under=80）；
- 首次远端运行结果：**待推送后回填**（运行/停止服务类操作需用户确认后执行）。

---

## 6. 当前总体状态（大白话）

代码写完了、测试全绿、规范检查零问题、仪表盘在本地用"无头模式"完整跑过一遍训练集和测试集。现在就差两件事：等你点头后推送到 GitHub 触发第一次 CI，以及由你决定是否现在启动仪表盘在浏览器里实际点一点。
