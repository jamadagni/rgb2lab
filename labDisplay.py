from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rgb2lab_int import *

class LabGraph(QLabel):

    def __init__(self, labParent, fixedValName, makeTableFn, var1Name, var1Min, var1Max, var2Name, var2Min, var2Max, transpose = False):

        assert var1Max > var1Min
        assert var2Max > var2Min

        QLabel.__init__(self)
        self.setFrameShape(QFrame.StyledPanel)

        self.labParent = labParent
        self.fixedValName = fixedValName
        self.makeTableFn = makeTableFn
        self.var1Name = var1Name
        self.var1Min = var1Min
        self.var1Max = var1Max
        self.var2Name = var2Name
        self.var2Min = var2Min
        self.var2Max = var2Max
        self.noTranspose = not transpose

        self.var1Span = var1Max - var1Min + 1
        self.var2Span = var2Max - var2Min + 1

        if self.noTranspose:
            self.hSize = self.var1Span ; self.vSize = self.var2Span
        else:
            self.hSize = self.var2Span ; self.vSize = self.var1Span
        self.setFixedSize(self.hSize, self.vSize)
        self.image = QImage(self.hSize, self.vSize, QImage.Format_ARGB32)

        t = self.redrawImageTimer = QTimer() # to delay redraw to avoid costly recalc while typing, fast spinning etc
        t.setInterval(100) # msecs
        t.timeout.connect(self.redrawImage)

        self.values = None

    def redrawIfNeeded(self):
        if self.values is None: # initial draw
            self.values = self.labParent.values.copy()
            self.redrawImage()
        elif self.values == self.labParent.values:
            return # no redraw at all
        else:
            prevFixedVal = self.values[self.fixedValName]
            self.values = self.labParent.values.copy()
            if prevFixedVal == self.labParent.values[self.fixedValName]:
                self.redrawPixmap() # no redrawImage
            else:
                self.redrawImageTimer.start()

    def redrawImage(self):
        self.redrawImageTimer.stop()
        fixedVal = self.values[self.fixedValName]
        table = self.makeTableFn(fixedVal)
        for var1 in range(self.var1Span):
            for var2 in range(self.var2Span):
                rgb = table[var1][var2]
                if self.noTranspose:
                    x = var1 ; y = self.var2Span - 1 - var2
                else:
                    x = var2 ; y = self.var1Span - 1 - var1
                # varSpan - 1 - var used above for second var since it ascends upwards whereas Y coordinates increases downwards
                self.image.setPixel(x, y, qRgb(rgb.r, rgb.g, rgb.b) if rgb.valid else Qt.transparent)
        self.redrawPixmap()

    def redrawPixmap(self):
        pixmap = QPixmap.fromImage(self.image)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.noTranspose:
            target = QPoint(self.values[self.var1Name] - self.var1Min, self.var2Max - self.values[self.var2Name])
        else:
            target = QPoint(self.values[self.var2Name] - self.var2Min, self.var1Max - self.values[self.var1Name])
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

    def __init__(self, mainWindow):

        QWidget.__init__(self)
        self.mainWindow = mainWindow

        self.graphL_ab = LabGraph(self, "L", makeTableL_ab, "A", -128, +128, "B", -128, +128)
        self.graphA    = LabGraph(self, "A", makeTableA   , "L",    0,  100, "B", -128, +128)
        self.graphB    = LabGraph(self, "B", makeTableB   , "L",    0,  100, "A", -128, +128)
        self.graphL_ch = LabGraph(self, "L", makeTableL_ch, "C",    0,  180, "H",    0,  359, transpose = True)
        self.graphC    = LabGraph(self, "C", makeTableC   , "L",    0,  100, "H",    0,  359, transpose = True)
        self.graphH    = LabGraph(self, "H", makeTableH   , "L",    0,  100, "C",    0,  180, transpose = True)
        self.allGraphs = (self.graphL_ab, self.graphA, self.graphB, self.graphL_ch, self.graphC, self.graphH)

        l = self.leftBottomLayout = QHBoxLayout()
        l.addWidget(self.graphA)
        l.addWidget(self.graphB)
        l = self.leftLayout = QVBoxLayout()
        l.addWidget(self.graphL_ab)
        l.addLayout(self.leftBottomLayout)

        l = self.rightLayout = QVBoxLayout()
        l.addWidget(self.graphL_ch)
        l.addWidget(self.graphC)
        l.addWidget(self.graphH, 0, Qt.AlignHCenter)

        l = self.mainLayout = QHBoxLayout()
        l.addLayout(self.leftLayout)
        l.addLayout(self.rightLayout)
        self.setLayout(l)

        self.values = None
        self.isShown = False

    def closeEvent(self, event):
        self.mainWindow.showGraphsCheckBox.setChecked(False)

    def showEvent(self, event):
        self.isShown = True
        self.redraw()

    def hideEvent(self, event):
        self.isShown = False

    def setValues(self, L, A, B, C, H):
        self.values = dict(zip("LABCH", (L, A, B, C, H)))
        if self.isShown: self.redraw()

    def redraw(self):
        for g in self.allGraphs: g.redrawIfNeeded()
