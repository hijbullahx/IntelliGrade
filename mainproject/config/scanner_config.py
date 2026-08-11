from typing import Dict, Any

class ScannerConfig:
    RENDER_DPI = 300
    MIN_IMAGE_BYTES = 500  # Filter out tiny 1x1 icons
    LINE_CLUSTERING_TOLERANCE_PX = 12.0
    LINE_ISOLATION_MARGIN_PCT = 0.02
    TABLE_CELL_PADDING_PX = 4
    FIGURE_THUMBNAIL_SIZE = (300, 300)
    MAX_HEADING_Y_PCT = 0.35  # Top region scan window for Vision LLM header fallback

def get_scanner_config() -> Dict[str, Any]:
    return {
        "dpi": ScannerConfig.RENDER_DPI,
        "line_clustering_tolerance_px": ScannerConfig.LINE_CLUSTERING_TOLERANCE_PX,
        "figure_thumbnail_size": ScannerConfig.FIGURE_THUMBNAIL_SIZE,
        "max_heading_y_pct": ScannerConfig.MAX_HEADING_Y_PCT,
    }
