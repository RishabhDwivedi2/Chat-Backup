# app/models/enums.py

from enum import Enum as PyEnum

class ComponentType(str, PyEnum):
    TEXT = "text"
    TABLE = "table"
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    RADAR_CHART = "radar_chart"
    AREA_CHART = "area_chart"
    SCATTER_PLOT = "scatter_plot"
    TREE_MAP = "tree_map"
    HEATMAP = "heatmap"
    CARD = "card"
    METRIC = "metric"