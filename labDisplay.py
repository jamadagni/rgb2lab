from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rgb2lab_int import *
from time import process_time
from sys import stderr

class LabDisplay(QLabel):

    def __init__(self):
        QLabel.__init__(self)
        self.setMinimumSize(257, 257)
        self.image = QImage(257, 257, QImage.Format_ARGB32)
        self.timer = QTimer() # to delay redraw to avoid costly recalc while typing
        self.timer.setInterval(250) # msecs
        self.timer.timeout.connect(self.redraw)

    def setLab(self, L, A, B):
        self.lab = (L, A, B)
        self.lch = lchFromLabInt(L, A, B)
        self.prepForRedraw()

    def setLch(self, l, c, h):
        self.lab = labFromLchInt(l, c, h)
        self.lch = (l, c, h)
        self.prepForRedraw()

    def prepForRedraw(self):
        self.setPixmap(QPixmap())
        self.timer.start()

    def redraw(self):
        self.timer.stop()
        L = self.lab[0]
        L_ = L * 255 / 100
        lColor = qRgba(L_, L_, L_, 127)
        LC = ((L + 50) % 101) * 255 / 100
        lCounterColor = qRgba(LC, LC, LC, 127)
        t = process_time()
        for A in range(-128, 129):
            for B in range(-128, 129):
                rgb = rgbFromLabInt(L, A, B)
                self.image.setPixel(A + 128, 256 - (B + 128), lColor if -1 in rgb else qRgb(*rgb))
        print("{:.2f} secs used for updating Lab image".format(process_time() - t), file = stderr)
        p = QPainter(self.image)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(lCounterColor)
        L, A, B = self.lab
        l, c, h = self.lch
        center = QPoint(128, 128)
        target = QPoint(A + 128, 256 - (B + 128))
        p.drawLine(center, target)
        p.drawEllipse(center, c, c)
        p.drawEllipse(target, 10, 10)
        self.setPixmap(QPixmap.fromImage(self.image))
