from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtWidgets import QWidget

class ColorDisplay(QWidget):

    def __init__(self, width = 100, height = 100, fixed = False):
        QWidget.__init__(self)
        self.color = QColor(Qt.transparent)
        if fixed:
            self.setFixedSize(width, height)
        else:
            self.setMinimumSize(width, height)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setBrush(QBrush(self.color))
        p.drawRect(self.rect())

    def setColor(self, c):
        self.color = c
        self.update()
