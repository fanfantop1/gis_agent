"""主窗口 — 三分栏布局."""
from __future__ import annotations

import asyncio
import sys

import qasync
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QStatusBar,
)

from gis_agent.ui.chat_panel import ChatPanel
from gis_agent.ui.layer_panel import LayerPanel
from gis_agent.ui.map_view import MapView
from gis_agent.utils.config import AppConfig, load_config
from gis_agent.utils.logger import logger


class MainWindow(QMainWindow):
    """主窗口 — 左侧聊天、中央地图、右侧图层."""

    def __init__(self, config: AppConfig | None = None) -> None:
        super().__init__()
        self._config = config or load_config()

        self.setWindowTitle(f"{self._config.app_name} v{self._config.version}")
        self.resize(1400, 900)

        self._setup_menubar()
        self._setup_central()
        self._setup_statusbar()

        # 欢迎消息
        self._chat.append_system_message(
            "欢迎使用 GIS Agent！"
            "你可以用自然语言处理地理数据。\n"
            "示例：\n"
            "• 「加载 road.shp 并显示在地图上」\n"
            "• 「计算道路 500 米缓冲区」\n"
            "• 「分析缓冲区内有多少个 POI」"
        )

        logger.info(f"{self._config.app_name} v{self._config.version} 启动完成")

    def _setup_menubar(self) -> None:
        menubar = self.menuBar()

        # 文件
        file_menu = menubar.addMenu("文件(&F)")

        new_action = QAction("新建项目", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_action = QAction("打开项目...", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        save_action = QAction("保存项目", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        import_action = QAction("导入数据...", self)
        import_action.setShortcut("Ctrl+I")
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设置
        settings_menu = menubar.addMenu("设置(&S)")
        settings_menu.addAction(QAction("LLM 设置...", self))

        # 帮助
        help_menu = menubar.addMenu("帮助(&H)")
        help_menu.addAction(QAction("关于", self))

    def _setup_central(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # 左侧：聊天面板 (30%)
        self._chat = ChatPanel()
        self._chat.message_sent.connect(self._on_user_message)
        splitter.addWidget(self._chat)

        # 中央：地图视图 (50%)
        self._map = MapView()
        splitter.addWidget(self._map)

        # 右侧：图层面板 (20%)
        self._layer = LayerPanel()
        splitter.addWidget(self._layer)

        # 初始比例
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 5)
        splitter.setStretchFactor(2, 2)
        splitter.setSizes([420, 700, 280])

        # 地图 ↔ 状态栏联动
        self._map.bridge.map_clicked.connect(self._on_map_clicked)
        self._map.bridge.map_moved.connect(self._on_map_moved)
        self._map.bridge.feature_clicked.connect(self._on_feature_clicked)

    def _setup_statusbar(self) -> None:
        status = QStatusBar()
        status.showMessage("就绪 | Ollama 未连接 | 项目: 未保存")
        self.setStatusBar(status)

    # ── 属性 ──────────────────────────────

    @property
    def chat_panel(self) -> ChatPanel:
        return self._chat

    @property
    def map_view(self) -> MapView:
        return self._map

    @property
    def layer_panel(self) -> LayerPanel:
        return self._layer

    # ── 地图事件 ────────────────────────────

    def _on_map_clicked(self, lat: float, lng: float) -> None:
        self.statusBar().showMessage(f"点击位置: {lat:.5f}, {lng:.5f}")

    def _on_map_moved(self, lat: float, lng: float, zoom: float) -> None:
        self.statusBar().showMessage(
            f"中心: {lat:.4f}, {lng:.4f} | 缩放: {int(zoom)}"
        )

    def _on_feature_clicked(self, layer_id: str, properties_json: str) -> None:
        self._chat.append_system_message(
            f"点击了图层 [{layer_id}] 要素\n属性: {properties_json}"
        )

    # ── 消息处理 ───────────────────────────

    def _on_user_message(self, text: str) -> None:
        """用户发送消息 — 后续接入 Agent 循环."""
        self._chat.append_system_message(f"收到: 「{text}」\n（Agent 未连接，此功能将在下一步实现）")
