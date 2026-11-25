"""Simple MapView widget for STRIX ONE (placeholder table display)."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem

class MapView(QWidget):
    def __init__(self, title: str, row_bins, col_bins, vmin: float, vmax: float):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>{title}</b>  (Alpha-N: TPS% × RPM)"))
        self.table = QTableWidget(len(row_bins), len(col_bins))
        self.table.setHorizontalHeaderLabels([str(c) for c in col_bins])
        self.table.setVerticalHeaderLabels([f"{r}%" for r in row_bins])
        # Fill with midpoint values
        mid = (vmin + vmax) / 2
        for r in range(len(row_bins)):
            for c in range(len(col_bins)):
                self.table.setItem(r, c, QTableWidgetItem(f"{mid:.1f}"))
        layout.addWidget(self.table)
