"""图层面板组件."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LayerPanel(QWidget):
    """图层面板：图层列表 + 管理按钮."""

    layer_visibility_changed = Signal(str, bool)  # layer_name, visible
    layer_removed = Signal(str)  # layer_name

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self.setLayout(layout)

        # 标题
        header = QLabel("图层")
        header.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        layout.addWidget(header)

        # 图层列表
        self._list = QListWidget()
        self._list.setFont(QFont("Microsoft YaHei", 10))
        self._list.setAlternatingRowColors(True)
        layout.addWidget(self._list, stretch=1)

        # 按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)

        self._add_btn = QPushButton("+")
        self._add_btn.setToolTip("添加图层")
        self._add_btn.setFixedWidth(30)
        btn_layout.addWidget(self._add_btn)

        self._remove_btn = QPushButton("-")
        self._remove_btn.setToolTip("移除选中图层")
        self._remove_btn.setFixedWidth(30)
        self._remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self._remove_btn)

        self._zoom_btn = QPushButton("⊕")
        self._zoom_btn.setToolTip("缩放到图层范围")
        self._zoom_btn.setFixedWidth(30)
        btn_layout.addWidget(self._zoom_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def add_layer(self, name: str, visible: bool = True) -> None:
        """添加图层到列表."""
        item = QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(
            Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
        )
        self._list.addItem(item)

    def remove_layer(self, name: str) -> None:
        """按名称移除图层."""
        for i in range(self._list.count()):
            if self._list.item(i).text() == name:
                self._list.takeItem(i)
                break

    def _remove_selected(self) -> None:
        """移除选中图层."""
        for item in self._list.selectedItems():
            name = item.text()
            self._list.takeItem(self._list.row(item))
            self.layer_removed.emit(name)

    def clear_layers(self) -> None:
        """清空所有图层."""
        self._list.clear()
