"""Minimal LiveStrip widget for STRIX ONE."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class LiveStrip(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(self)
        self.labels = {}
        for name in ["RPM", "TPS %", "Baro", "CLT", "IAT", "Sync", "PW"]:
            lbl = QLabel(f"{name}: ---")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold; padding: 4px;")
            layout.addWidget(lbl)
            self.labels[name] = lbl

    def update_live(self, data: dict):
        self.labels["RPM"].setText(f"RPM: {data.get('rpm', 0)}")
        self.labels["TPS %"].setText(f"TPS: {data.get('tps', 0):.1f}%")
        self.labels["Baro"].setText(f"Baro: {data.get('baro', 0):.0f}")
        self.labels["CLT"].setText(f"CLT: {data.get('ect', 0):.0f}°C")
        self.labels["IAT"].setText(f"IAT: {data.get('iat', 0):.0f}°C")
        self.labels["Sync"].setText("Sync: YES" if data.get('sync') else "Sync: NO")
        self.labels["PW"].setText(f"PW: {data.get('pw', 0):.2f} ms")
