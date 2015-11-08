from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rgb2lab_int import *

class LabGraph(QWidget):

    def __init__(self, labParent, makeTableFn, fixedValName, var1Name, var1Min, var1Max, var2Name, var2Min, var2Max):

        assert var1Max > var1Min
        assert var2Max > var2Min

        QWidget.__init__(self)

        self.labParent = labParent
        self.makeTableFn = makeTableFn
        self.fixedValName = fixedValName
        self.var1Name = var1Name
        self.var1Min = var1Min
        self.var1Max = var1Max
        self.var2Name = var2Name
        self.var2Min = var2Min
        self.var2Max = var2Max

        self.var1Span = var1Max - var1Min + 1
        self.var2Span = var2Max - var2Min + 1
        self.totalPoints = self.var1Span * self.var2Span

        self.image = QImage(self.var1Span, self.var2Span, QImage.Format_ARGB32)

        t = self.redrawImageTimer = QTimer() # to delay redraw to avoid costly recalc while typing, fast spinning etc
        t.setInterval(100) # msecs
        t.timeout.connect(self.redrawImage)

        w = self.graph = QLabel()
        w.setFixedSize(self.var1Span, self.var2Span)
        w.setFrameShape(QFrame.StyledPanel)

        self.captionFmtString = "{} = {{}}; X: {} [{} to {}], Y: {} [{} to {}]\n{{}}% ({{}} of {}) points in gamut".format(
                                fixedValName, var1Name, var1Min, var1Max, var2Name, var2Min, var2Max, self.totalPoints)
        w = self.caption = QLabel()
        w.setAlignment(Qt.AlignHCenter)

        l = self.mainLayout = QVBoxLayout()
        l.addWidget(self.graph, 0, Qt.AlignHCenter)
        l.addWidget(self.caption, 0, Qt.AlignHCenter)
        self.setLayout(l)

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
        self.caption.setText(self.captionFmtString.format(fixedVal, round(100 * table.inGamutCount / self.totalPoints, 2), table.inGamutCount))
        for var1 in range(self.var1Span):
            for var2 in range(self.var2Span):
                rgb = table[var1][var2]
                self.image.setPixel(var1, self.var2Span - 1 - var2, qRgb(rgb.r, rgb.g, rgb.b) if rgb.valid else Qt.transparent)
                # var2Span - 1 - var2 needed since we want var2 to increase upwards but Y value increases downwards
        self.redrawPixmap()

    def redrawPixmap(self):
        pixmap = QPixmap.fromImage(self.image)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        target = QPoint(self.values[self.var1Name] - self.var1Min, self.var2Max - self.values[self.var2Name])
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
        self.graph.setPixmap(pixmap)

class LabDisplay(QWidget):

    def __init__(self, mainWindow):

        QWidget.__init__(self)
        self.setWindowTitle("RGB2LAB GUI: LABCH Graphs")

        self.mainWindow = mainWindow

        self.graphL_AB = LabGraph(self, makeTableL_AB, "L", "A", -128, +128, "B", -128, +128)
        self.graphA_BL = LabGraph(self, makeTableA_BL, "A", "B", -128, +128, "L",    0,  100)
        self.graphB_AL = LabGraph(self, makeTableB_AL, "B", "A", -128, +128, "L",    0,  100)
        self.graphL_HC = LabGraph(self, makeTableL_HC, "L", "H",    0,  359, "C",    0,  180)
        self.graphC_HL = LabGraph(self, makeTableC_HL, "C", "H",    0,  359, "L",    0,  100)
        self.graphH_CL = LabGraph(self, makeTableH_CL, "H", "C",    0,  180, "L",    0,  100)
        self.allGraphs = (self.graphL_AB, self.graphA_BL, self.graphB_AL, self.graphL_HC, self.graphC_HL, self.graphH_CL)

        l = self.leftLayout = QVBoxLayout()
        l.addWidget(self.graphL_AB)
        l.addWidget(self.graphA_BL)
        l.addWidget(self.graphB_AL)

        l = self.rightLayout = QVBoxLayout()
        l.addWidget(self.graphL_HC)
        l.addWidget(self.graphC_HL)
        l.addWidget(self.graphH_CL)

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
