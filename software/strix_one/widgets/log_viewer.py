"""Stub widget – full implementation available in original TorquEFI STRIX.
Adapted/simplified for STRIX ONE single-cylinder Alpha-N.
"""
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class Stub(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("STRIX ONE – feature simplified for single-cylinder Alpha-N"))
