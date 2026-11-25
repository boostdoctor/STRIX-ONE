"""STRIX ONE constants – single-cylinder Alpha-N only.
Layout and helpers match TorquEFI STRIX V2 for visual compatibility.
"""
import math

STRIX_VERSION = "ONE-1.0"
STRIX_PROTO = 1

# Single-cylinder Alpha-N maps
ROWS = 12          # TPS load axis
COLS = 16          # RPM axis
BAUD = 115200
TELEM_HZ = 40

VE_REF_MS = 2.5
ADV_MIN, ADV_MAX = -10, 45
INJ_MIN, INJ_MAX = 0.0, 20.0

# RPM axis for single cylinder
RPM_BINS = [500 + c * 500 for c in range(COLS)]

SETTINGS_FILE = "strix_one_settings.json"
DEVICE_ID_FILE = "device_id.json"
TCAL_VERSION = 1

# Live strip
ALWAYS_STRIP = ["rpm", "tps", "baro", "ect", "iat", "sync", "pw"]
OPTIONAL_STRIP = ["bat", "afr", "ign", "load", "tooth"]

# Sensors (simplified for single-cylinder Alpha-N)
MAP_SENSORS = [
    ("Barometric (MAP input)", 110),
    ("Bosch 1.1 bar", 115),
    ("GM 1 bar", 105),
]
TEMP_SENSORS = [
    ("NTC 2.2k", None),
    ("NTC 10k", None),
]
O2_MODES = ("Disabled", "Narrowband", "Wideband")

MAP_KPA_MIN = 80
MAP_KPA_MAX_DEFAULT = 110
MAP_KPA_MAX_LIMIT = 120

# Default compensation tables (stubs for single cylinder)
DEFAULT_ECT_COMP = [[i * 100, 0, 0] for i in range(14)]
DEFAULT_IAT_COMP = [[i * 100, 0, 0] for i in range(14)]
DEFAULT_BAT_COMP = [[80 + i * 8, 0, 0] for i in range(10)]

# Firing orders (single cylinder only)
FIRING_ORDERS_BY_CYL = {1: ["1"]}
ALL_FIRING_ORDERS = ["1"]


# Trigger wheel profiles (single-cylinder set)
WHEEL_PROFILES = {
    0: {"name": "12-1", "teeth": 12, "missing": 1},
    1: {"name": "Single Tooth", "teeth": 1, "missing": 0},
    2: {"name": "36-1", "teeth": 36, "missing": 1},
    3: {"name": "24-1", "teeth": 24, "missing": 1},
    4: {"name": "24-2", "teeth": 24, "missing": 2},
}


def make_tps_bins() -> list[int]:
    """TPS load axis 0…100 % (Alpha-N)."""
    if ROWS <= 1:
        return [0]
    step = 100.0 / (ROWS - 1)
    return [int(round(i * step)) for i in range(ROWS)]

def make_map_bins(kpa_max: int = 110, kpa_min: int = 80) -> list[int]:
    """Barometric range (MAP input used as baro)."""
    step = (kpa_max - kpa_min) / max(1, ROWS - 1)
    return [int(round(kpa_min + i * step)) for i in range(ROWS)]

TPS_BINS = make_tps_bins()

TRIGGER_MODES = {
    0: "12-1",
    1: "Single Tooth",
    2: "36-1",
    3: "24-1",
    4: "24-2",
}

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1e1e1e; color: #e0e0e0; font-family: Segoe UI, sans-serif; }
QPushButton { background-color: #333; border: 1px solid #555; padding: 5px 14px; border-radius: 3px; }
QPushButton:hover { background-color: #444; }
QComboBox, QSpinBox, QLineEdit { background-color: #2a2a2a; border: 1px solid #555; padding: 3px; }
QTabWidget::pane { border: 1px solid #444; background: #1e1e1e; }
QTabBar::tab { background: #2a2a2a; padding: 6px 16px; }
QTabBar::tab:selected { background: #3a3a3a; }
QTableWidget { background-color: #252525; gridline-color: #444; }
QHeaderView::section { background-color: #333; padding: 4px; }
QStatusBar { background: #2a2a2a; }
"""

def suggested_ve_map(rows: int = ROWS, cols: int = COLS) -> list[list[float]]:
    """Alpha-N VE % base map (TPS × RPM) for single cylinder."""
    out = []
    for r in range(rows):
        lf = r / max(1, rows - 1)
        row = []
        for c in range(cols):
            rf = c / max(1, cols - 1)
            peak = 1.0 - abs(rf - 0.45) * 1.5
            peak = max(0.0, peak)
            ve = 55.0 + lf * 35.0 + peak * 10.0
            if rf > 0.75:
                ve -= (rf - 0.75) * 15.0
            ve = max(40.0, min(110.0, ve))
            row.append(round(ve, 1))
        out.append(row)
    return out

def suggested_adv_map(rows: int = ROWS, cols: int = COLS) -> list[list[int]]:
    """Ignition advance (° BTDC) for single cylinder."""
    out = []
    for r in range(rows):
        lf = r / max(1, rows - 1)
        row = []
        for c in range(cols):
            rf = c / max(1, cols - 1)
            adv = 10.0 + rf * 20.0 - lf * 12.0 + (0.5 - abs(rf - 0.4)) * 6.0
            adv = max(5, min(40, int(round(adv))))
            row.append(adv)
        out.append(row)
    return out

def suggested_afr_map(rows: int = ROWS, cols: int = COLS) -> list[list[float]]:
    out = []
    for r in range(rows):
        lf = r / max(1, rows - 1)
        row = []
        for c in range(cols):
            afr = 14.7 - lf * 2.0
            afr = max(12.0, min(15.0, afr))
            row.append(round(afr, 1))
        out.append(row)
    return out

def suggested_idle_fuel_map() -> list[list[float]]:
    return [[0.0]*5 for _ in range(5)]

def suggested_idle_ign_map() -> list[list[float]]:
    return [[0.0]*5 for _ in range(5)]

def suggested_inj_ms_map(rows: int = ROWS, cols: int = COLS, **kwargs) -> list[list[float]]:
    """Not used in VE-only mode; returns empty-ish map."""
    return [[2.5]*cols for _ in range(rows)]

def suggested_vvt_map(rows: int = 8, cols: int = 8, exhaust: bool = False) -> list[list[float]]:
    return [[0.0]*cols for _ in range(rows)]

def suggested_boost_map(rows: int = 8, cols: int = 8, closed_loop: bool = True) -> list[list[float]]:
    return [[0.0]*cols for _ in range(rows)]
