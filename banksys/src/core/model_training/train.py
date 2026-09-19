"""模型训练命令行入口。

运行方式（在 banksys/ 项目根目录）：

    .\\envbank\\Scripts\\python.exe -m src.core.model_training.train

可选参数：
    --quick             跳过网格搜索，快速冒烟验证全链路
    --only 模型名 ...   只训练指定模型（可多选）
    --compare-duration  执行 duration 数据泄露对照实验
"""

from __future__ import annotations

import argparse
import json

from src.core.model_training.config import ModelTrainingConfig
from src.core.model_training.pipeline import TrainingOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="banksys 银行营销认购模型训练（M2）")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="跳过网格搜索，快速验证训练全链路",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        choices=ModelTrainingConfig().model_names,
        help="只训练指定的一个或多个模型",
    )
    parser.add_argument(
        "--compare-duration",
        action="store_true",
        help="额外执行 duration 数据泄露对照实验",
    )
    return parser


def main() -> None:
    """训练主流程。"""
    args = _build_parser().parse_args()
    config = ModelTrainingConfig()
    orchestrator = TrainingOrchestrator(config)

    report = orchestrator.run(
        model_names=tuple(args.only) if args.only else None,
        quick=args.quick,
    )

    logger.info("各模型测试集指标对比：")
    for name, result in report.results.items():
        assert result.metrics is not None
        assert result.benefit is not None
        metrics = result.metrics
        marker = "（入选最佳）" if name == report.best_model_name else ""
        logger.info(
            "  %s%s：ROC-AUC=%.4f，PR-AUC=%.4f，F1=%.4f，净收益=%.0f 元",
            name,
            marker,
            metrics.roc_auc,
            metrics.pr_auc,
            metrics.f1,
            result.benefit.net_benefit,
        )

    if args.compare_duration:
        comparison = orchestrator.compare_duration_leakage()
        comparison_path = config.models_dir / "duration_leakage_comparison.json"
        comparison_path.write_text(
            json.dumps(comparison, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.warning("duration 泄露对照结果已保存：%s", comparison_path)


if __name__ == "__main__":
    main()
