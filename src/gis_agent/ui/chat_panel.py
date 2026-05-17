"""聊天面板组件."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class ChatPanel(QWidget):
    """聊天面板：消息展示 + 输入框 + 发送按钮."""

    message_sent = Signal(str)  # 用户发送消息信号

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self.setLayout(layout)

        # 消息展示区
        self._message_view = QTextBrowser()
        self._message_view.setOpenExternalLinks(True)
        self._message_view.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(self._message_view, stretch=1)

        # 输入区
        input_layout = QHBoxLayout()
        input_layout.setSpacing(4)

        self._input = QLineEdit()
        self._input.setPlaceholderText("输入地理问题，例如：加载 road.shp 并显示缓冲区...")
        self._input.setFont(QFont("Microsoft YaHei", 10))
        self._input.returnPressed.connect(self._send)
        input_layout.addWidget(self._input, stretch=1)

        self._send_btn = QPushButton("发送")
        self._send_btn.setFont(QFont("Microsoft YaHei", 10))
        self._send_btn.clicked.connect(self._send)
        input_layout.addWidget(self._send_btn)

        layout.addLayout(input_layout)

    def _send(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._append_message("你", text, "#0078d4")
        self.message_sent.emit(text)

    def append_user_message(self, text: str) -> None:
        self._append_message("你", text, "#0078d4")

    def append_agent_message(self, text: str) -> None:
        self._append_message("GIS Agent", text, "#107c10")

    def append_system_message(self, text: str) -> None:
        self._append_message("系统", text, "#888888")

    def append_tool_message(self, tool_name: str, text: str) -> None:
        self._append_message(f"🔧 {tool_name}", text, "#d83b01")

    def _append_message(self, sender: str, text: str, color: str) -> None:
        self._message_view.append(
            f'<p><b style="color:{color}">{sender}:</b> '
            f'<span style="color:#333">{text}</span></p>'
        )
        self._message_view.verticalScrollBar().setValue(
            self._message_view.verticalScrollBar().maximum()
        )

    def clear(self) -> None:
        self._message_view.clear()
