"""地图桥接 — QWebChannel 双向通信."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView


class MapBridge(QObject):
    """QWebChannel 桥接对象：JS ↔ Python."""

    # JS → Python 信号
    map_clicked = Signal(float, float)          # lat, lng
    map_moved = Signal(float, float, float)     # lat, lng, zoom
    feature_clicked = Signal(str, str)           # layer_id, properties_json

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    # ── 供 JS 调用的槽 ──

    @Slot(float, float)
    def onMapClick(self, lat: float, lng: float) -> None:
        self.map_clicked.emit(lat, lng)

    @Slot(float, float, float)
    def onMapMoveEnd(self, lat: float, lng: float, zoom: float) -> None:
        self.map_moved.emit(lat, lng, zoom)

    @Slot(str, str)
    def onFeatureClick(self, layer_id: str, properties_json: str) -> None:
        self.feature_clicked.emit(layer_id, properties_json)


class MapWidget(QWebEngineView):
    """封装了 Leaflet 地图的 QWebEngineView."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._bridge = MapBridge(self)
        self._channel = QWebChannel(self)
        self._channel.registerObject("bridge", self._bridge)
        self.page().setWebChannel(self._channel)

        # 允许本地文件访问远程资源
        settings = self.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        self._load_map_page()

    def _load_map_page(self) -> None:
        html_path = Path(__file__).parent / "static" / "map.html"
        if html_path.exists():
            self.setUrl(QUrl.fromLocalFile(str(html_path.resolve())))
        else:
            self.setHtml("<h2>地图页面未找到</h2>")

    # ── 便捷方法 ──

    @property
    def bridge(self) -> MapBridge:
        return self._bridge

    def add_geojson(self, geojson_str: str, layer_id: str, style: dict | None = None) -> None:
        """向地图添加 GeoJSON 图层."""
        import json
        style_json = json.dumps(style) if style else "null"
        escaped = geojson_str.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        js = f"addGeoJSON('{escaped}', '{layer_id}', {style_json});"
        self.page().runJavaScript(js)

    def remove_layer(self, layer_id: str) -> None:
        self.page().runJavaScript(f"removeLayer('{layer_id}');")

    def set_layer_visibility(self, layer_id: str, visible: bool) -> None:
        v = "true" if visible else "false"
        self.page().runJavaScript(f"setLayerVisibility('{layer_id}', {v});")

    def zoom_to_layer(self, layer_id: str) -> None:
        self.page().runJavaScript(f"zoomToLayer('{layer_id}');")

    def set_center(self, lat: float, lng: float, zoom: int = 12) -> None:
        self.page().runJavaScript(f"setMapCenter({lat}, {lng}, {zoom});")

    def fly_to(self, lat: float, lng: float, zoom: int = 16) -> None:
        self.page().runJavaScript(f"flyTo({lat}, {lng}, {zoom});")

    def change_basemap(self, url: str, attribution: str = "") -> None:
        self.page().runJavaScript(f"changeBasemap('{url}', '{attribution}');")

    def get_map_state(self, callback) -> None:
        """异步获取当前地图状态."""
        self.page().runJavaScript("getMapState();", callback)
