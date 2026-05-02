from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Signal

class QLabelClickable(QLabel):
    clicked = Signal(int, int)

    def mousePressEvent(self, ev):
        pos = ev.position().toPoint()
        self.clicked.emit(pos.x(), pos.y())
widgets = [QLabelClickable]
