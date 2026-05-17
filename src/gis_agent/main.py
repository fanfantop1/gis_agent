"""GIS Agent 应用入口."""
from __future__ import annotations

import asyncio
import sys

import qasync
from PySide6.QtWidgets import QApplication

from gis_agent.ui.main_window import MainWindow
from gis_agent.utils.logger import setup_logger


def main() -> None:
    setup_logger(level="INFO")

    app = QApplication(sys.argv)
    app.setApplicationName("GIS Agent")

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
