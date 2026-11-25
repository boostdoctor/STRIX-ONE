"""STRIX ONE constants – single-cylinder Alpha-N only variant."""
import math

STRIX_VERSION = "ONE-1.0"
STRIX_PROTO = 1

# Single-cylinder Alpha-N maps (TPS % load)
ROWS = 12          # TPS load axis
COLS = 16          # RPM axis (simplified vs original 22)
BAUD = 115200
TELEM_HZ = 40

VE_REF_MS = 2.5

ADV_MIN, ADV_MAX = -10, 45
INJ_MIN, INJ_MAX = 0.0, 20.0

# RPM axis
RPM_BINS = [500 + c * 500 for c in range(COLS)]  # 500 … 8000

def make_tps_bins() -> list[int]:
    """TPS load axis 0…100 %."""
    if ROWS <= 1:
        return [0]
    step = 100.0 / (ROWS - 1)
    return [int(round(i * step)) for i in range(ROWS)]

TPS_BINS = make_tps_bins()

# Trigger modes matching firmware
TRIGGER_MODES = {
    0: "12-1",
    1: "Single Tooth",
    2: "36-1",
    3: "24-1",
    4: "24-2",
}

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1e1e1e; color: #e0e0e0; }
QPushButton { background-color: #333; border: 1px solid #555; padding: 4px 12px; }
QPushButton:hover { background-color: #444; }
QComboBox, QSpinBox { background-color: #2a2a2a; border: 1px solid #555; }
QTabWidget::pane { border: 1px solid #444; }
"""
