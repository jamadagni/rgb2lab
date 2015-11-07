from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rgb2lab_int import *

class _LABCH:
    def __init__(self, L, A, B, C, H):
        self.L = L ; self.A = A ; self.B = B ; self.C = C ; self.H = H
    def __str__(self):
        return "_LABCH(L = {}, A = {}, B = {}, C = {}, H = {})".format(self.L, self.A, self.B, self.C, self.H)
    def __eq__(self, other):
        return self.L == other.L and self.A == other.A and self.B == other.B and self.C == other.C and self.H == other.H
    def copy(self):
        return _LABCH(self.L, self.A, self.B, self.C, self.H)

class _LabGraphABC(QLabel):

    def __init__(self, labDisplay, hSize, vSize):
        QLabel.__init__(self)
        self.labDisplay = labDisplay
        self.setFixedSize(hSize, vSize)
        self.image = QImage(hSize, vSize, QImage.Format_ARGB32)
        t = self.redrawImageTimer = QTimer() # to delay redraw to avoid costly recalc while typing, fast spinning etc
        t.setInterval(100) # msecs
        t.timeout.connect(self.redrawImage)
        self.values = None # for redrawPixmap

    def redrawIfNeeded(self):
        raise NotImplementedError

    def redrawImage(self):
        raise NotImplementedError

    def redrawPixmap(self):
        raise NotImplementedError

class LabGraphL_ab(_LabGraphABC):

    def __init__(self, labDisplay):
        _LabGraphABC.__init__(self, labDisplay, 257, 257)

    def redrawIfNeeded(self):
        if self.values is None: # initial status
            self.values = self.labDisplay.values.copy()
            self.redrawImage()
        elif self.values == self.labDisplay.values:
            return # no redraw at all
        else:
            prevL = self.values.L
            self.values = self.labDisplay.values.copy()
            if prevL == self.labDisplay.values.L:
                self.redrawPixmap() # no redrawImage
            else:
                self.redrawImageTimer.start()

    def redrawImage(self):
        self.redrawImageTimer.stop()
        L = self.values.L
        tableL_ab = makeTableL_ab(L)
        for A in range(257):
            for B in range(257):
                rgb = tableL_ab[A][B]
                self.image.setPixel(A, 256 - B, qRgb(rgb.r, rgb.g, rgb.b) if rgb.valid else Qt.transparent)
        self.redrawPixmap()

    def redrawPixmap(self):
        pixmap = QPixmap.fromImage(self.image)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        target = QPoint(self.values.A + 128, 256 - (self.values.B + 128))
        painter.setPen(QColor(Qt.white))
        painter.drawEllipse(target, 11, 11) # outer circle with inner plus
        for end in (QPoint(4, 0), QPoint(0, 4)):
            painter.drawLine(target, target - end)
            painter.drawLine(target, target + end)
        painter.setPen(QColor(Qt.black)) # inner circle with outer ticks
        painter.drawEllipse(target, 9, 9)
        for start, end in ((QPoint(9, 0), QPoint(5, 0)), (QPoint(0, 9), QPoint(0, 4))):
            painter.drawLine(target - start, target - end)
            painter.drawLine(target + start, target + end)
        painter.end()
        self.setPixmap(pixmap)

class LabDisplay(QWidget):

    def __init__(self):

        QWidget.__init__(self)

        self.graphL_ab = LabGraphL_ab(self) # 257 A, 257 B
        self.allGraphs = (self.graphL_ab,)

        l = self.mainLayout = QHBoxLayout()
        l.addWidget(self.graphL_ab)
        self.setLayout(l)

        self.values = None

    def setValues(self, L, A, B, C, H):
        self.values = _LABCH(L, A, B, C, H)
        for g in self.allGraphs: g.redrawIfNeeded()
