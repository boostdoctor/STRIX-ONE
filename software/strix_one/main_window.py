"""STRIX ONE main window – exact layout style of TorquEFI STRIX, simplified for single-cylinder Alpha-N."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QLabel, QTabWidget, QStatusBar, QMessageBox, QApplication,
)

from strix_one.constants import BAUD, DARK_STYLE, TRIGGER_MODES, TPS_BINS, RPM_BINS
from strix_one.serial_worker import SerialWorker, list_serial_ports
from strix_one.protocol import default_live, parse_line
from strix_one.widgets.live_strip import LiveStrip
from strix_one.widgets.map_view import MapView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STRIX ONE – Single Cylinder Alpha-N")
        self.resize(1100, 750)
        self.setStyleSheet(DARK_STYLE)

        self.worker = None
        self.live = default_live()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Connection bar
        conn = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()
        conn.addWidget(QLabel("Port:"))
        conn.addWidget(self.port_combo)
        conn.addWidget(QPushButton("Refresh", clicked=self.refresh_ports))
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connect)
        conn.addWidget(self.connect_btn)
        layout.addLayout(conn)

        # Live strip
        self.live_strip = LiveStrip()
        layout.addWidget(self.live_strip)

        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # VE Map (Alpha-N: TPS vs RPM)
        self.ve_map = MapView("VE Map (Alpha-N)", TPS_BINS, RPM_BINS, 50, 120)
        tabs.addTab(self.ve_map, "VE Table")

        # Ignition Map
        self.ign_map = MapView("Ignition Advance", TPS_BINS, RPM_BINS, 0, 45)
        tabs.addTab(self.ign_map, "Ignition")

        # Trigger selection
        trig_page = QWidget()
        trig_layout = QVBoxLayout(trig_page)
        self.trigger_combo = QComboBox()
        self.trigger_combo.addItems(list(TRIGGER_MODES.values()))
        self.trigger_combo.currentIndexChanged.connect(self.on_trigger_changed)
        trig_layout.addWidget(QLabel("Trigger Mode (default 12-1):"))
        trig_layout.addWidget(self.trigger_combo)
        trig_layout.addStretch()
        tabs.addTab(trig_page, "Trigger")

        self.statusBar().showMessage("STRIX ONE ready – Alpha-N only, single cylinder")

        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_serial)
        self.timer.start(50)

    def refresh_ports(self):
        ports = list_serial_ports()
        self.port_combo.clear()
        self.port_combo.addItems(ports)

    def toggle_connect(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker = None
            self.connect_btn.setText("Connect")
            self.statusBar().showMessage("Disconnected")
        else:
            port = self.port_combo.currentText()
            if not port:
                QMessageBox.warning(self, "No port", "Select a serial port")
                return
            self.worker = SerialWorker(port, BAUD)
            self.worker.line_received.connect(self.on_line)
            self.worker.start()
            self.connect_btn.setText("Disconnect")
            self.statusBar().showMessage(f"Connected to {port}")

    def on_line(self, line: str):
        data = parse_line(line)
        if data:
            self.live.update(data)
            self.live_strip.update_live(self.live)

    def on_trigger_changed(self, idx: int):
        if self.worker:
            self.worker.send(f"T{idx}")
            self.statusBar().showMessage(f"Trigger set to {TRIGGER_MODES.get(idx, '?')}")

    def poll_serial(self):
        if self.worker:
            self.worker.send("S")  # request status

def main():
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()

if __name__ == "__main__":
    main()
