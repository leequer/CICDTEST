"""Streamlit 仪表盘无头冒烟测试。

使用官方 streamlit.testing.v1.AppTest 在进程内完整执行页面脚本，
验证默认渲染不抛异常、五个页签与关键指标均存在；无需启动 Web 服务。
"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

# 仪表盘脚本路径（banksys/src/frontend/dashboard/app.py）
APP_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "frontend" / "dashboard" / "app.py"
)


def test_dashboard_renders_without_exception() -> None:
    """测试：仪表盘默认加载训练集并完整渲染。"""
    app = AppTest.from_file(str(APP_PATH), default_timeout=30)
    app.run()

    assert not app.exception, f"页面渲染抛出异常：{app.exception}"
    # 五个业务页签必须全部存在
    assert len(app.tabs) == 5
    # 侧边栏存在动态筛选控件（多分类多选框 + 多个数值滑块）
    assert len(app.multiselect) >= 10
    assert len(app.slider) >= 10
    # 顶部关键指标（原始样本量、筛选后样本量等）
    metric_labels = [metric.label for metric in app.metric]
    assert "原始样本量" in metric_labels
    assert "筛选后认购率" in metric_labels


def test_dashboard_switch_to_test_dataset() -> None:
    """测试：切换到无标签测试集后不抛异常并给出提示。"""
    app = AppTest.from_file(str(APP_PATH), default_timeout=30)
    app.run()
    assert not app.exception

    # 侧边栏元素在 AppTest 列表中不保证位于首位，按标签定位数据集单选框
    dataset_radio = next(radio for radio in app.radio if radio.label == "选择数据集")
    dataset_radio.set_value("测试集 test.csv（无标签）").run()
    assert not app.exception, f"切换测试集后异常：{app.exception}"
