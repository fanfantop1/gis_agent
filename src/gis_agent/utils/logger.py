"""日志配置."""
from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def setup_logger(log_dir: Path | None = None, level: str = "INFO") -> None:
    """初始化日志系统."""
    logger.remove()

    # 控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=level,
        colorize=True,
    )

    # 文件输出
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_dir / "gis_agent_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            encoding="utf-8",
        )

    logger.info("日志系统初始化完成")
