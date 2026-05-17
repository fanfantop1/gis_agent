// GIS Agent — Leaflet 地图前端逻辑

let map;
let layers = {};       // { layerId: L.geoJSON }
let basemap;

// ── 初始化 ─────────────────────────────────
function initMap() {
    map = L.map('map', {
        center: [39.9, 116.4],
        zoom: 5,
        zoomControl: true,
    });

    // OSM 底图
    basemap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
    }).addTo(map);
}

// ── QWebChannel 连接 ────────────────────────
function connectBridge() {
    new QWebChannel(qt.webChannelTransport, function(channel) {
        window.bridge = channel.objects.bridge;

        // 地图点击 → Python
        map.on('click', function(e) {
            if (window.bridge) {
                window.bridge.onMapClick(e.latlng.lat, e.latlng.lng);
            }
        });

        // 地图移动结束 → 通知 Python
        map.on('moveend', function() {
            if (window.bridge) {
                var c = map.getCenter();
                window.bridge.onMapMoveEnd(c.lat, c.lng, map.getZoom());
            }
        });

        console.log('QWebChannel bridge connected');
    });
}

// ── Python 可调用的函数 ─────────────────────

function addGeoJSON(geojsonStr, layerId, style) {
    try {
        var geojson = JSON.parse(geojsonStr);
        var layerStyle = style ? JSON.parse(style) : {
            color: '#3388ff',
            weight: 2,
            fillColor: '#3388ff',
            fillOpacity: 0.2,
        };

        removeLayer(layerId);

        var geoLayer = L.geoJSON(geojson, {
            style: function() { return layerStyle; },
            onEachFeature: function(feature, lyr) {
                if (feature.properties) {
                    var props = JSON.stringify(feature.properties, null, 2);
                    lyr.bindPopup('<pre>' + props + '</pre>');
                }
                lyr.on('click', function() {
                    if (window.bridge) {
                        window.bridge.onFeatureClick(
                            layerId,
                            JSON.stringify(feature.properties || {})
                        );
                    }
                });
            },
        }).addTo(map);

        layers[layerId] = geoLayer;
        map.fitBounds(geoLayer.getBounds(), { padding: [30, 30] });
        console.log('Layer added: ' + layerId);
    } catch (e) {
        console.error('addGeoJSON error: ' + e.message);
    }
}

function removeLayer(layerId) {
    if (layers[layerId]) {
        map.removeLayer(layers[layerId]);
        delete layers[layerId];
        console.log('Layer removed: ' + layerId);
    }
}

function setLayerVisibility(layerId, visible) {
    if (layers[layerId]) {
        if (visible) {
            map.addLayer(layers[layerId]);
        } else {
            map.removeLayer(layers[layerId]);
        }
    }
}

function zoomToLayer(layerId) {
    if (layers[layerId]) {
        map.fitBounds(layers[layerId].getBounds(), { padding: [30, 30] });
    }
}

function setMapCenter(lat, lng, zoom) {
    map.setView([lat, lng], zoom || map.getZoom());
}

function changeBasemap(url, attribution) {
    if (basemap) {
        map.removeLayer(basemap);
    }
    basemap = L.tileLayer(url, {
        attribution: attribution || '',
        maxZoom: 19,
    }).addTo(map);
}

function flyTo(lat, lng, zoom) {
    map.flyTo([lat, lng], zoom || 16, { duration: 1.5 });
}

function getMapState() {
    var c = map.getCenter();
    return JSON.stringify({
        lat: c.lat,
        lng: c.lng,
        zoom: map.getZoom(),
    });
}

// ── 启动 ────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    connectBridge();
});
