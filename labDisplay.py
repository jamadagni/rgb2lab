from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rgb2lab_int import *

class LabDisplay(QLabel):

    def __init__(self):
        QLabel.__init__(self)
        self.setMinimumSize(257, 257)
        self.image = QImage(257, 257, QImage.Format_ARGB32)
        self.timer = QTimer() # to delay redraw to avoid costly recalc while typing, fast spinning etc
        self.timer.setInterval(100) # msecs
        self.timer.timeout.connect(self.redrawImage)
        self.values = (None,)

    def setValues(self, L, A, B, C, H):
        prevL = self.values[0]
        self.values = (L, A, B, C, H)
        if L != prevL:
            self.setPixmap(QPixmap())
            self.timer.start()
        else:
            self.redrawPixmap()

    def redrawImage(self):
        self.timer.stop()
        tableL_ab = makeTableL_ab(self.values[0])
        L = self.values[0]
        L_ = L * 255 / 100
        lColor = qRgba(L_, L_, L_, 127)
        for A in range(257):
            for B in range(257):
                rgb = tableL_ab[A][B]
                self.image.setPixel(A, 256 - B, qRgb(rgb.r, rgb.g, rgb.b) if rgb.valid else lColor)
        self.redrawPixmap()

    def redrawPixmap(self):
        L, A, B, c, h = self.values
        L_ = ((L + 50) % 101) * 255 / 100
        lCounterColor = qRgba(L_, L_, L_, 127)
        pixmap = QPixmap.fromImage(self.image)
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(lCounterColor)
        center = QPoint(128, 128)
        target = QPoint(A + 128, 256 - (B + 128))
        p.drawLine(center, target)
        p.drawEllipse(center, c, c)
        p.drawEllipse(target, 10, 10)
        p.end()
        self.setPixmap(pixmap)
