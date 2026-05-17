"""地图视图组件 — 嵌入 Leaflet 交互式地图."""
from __future__ import annotations

from gis_agent.bridge.map_bridge import MapWidget


class MapView(MapWidget):
    """地图主视图：QWebEngineView + Leaflet + QWebChannel 桥接."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
