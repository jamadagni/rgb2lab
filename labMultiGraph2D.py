# LabMultiGraph2D widget
# ======================
#
# visualize 2D slices of the CIELAB color space
# in cartesian and cylindrical representations
#
# Copyright (C) 2019, Shriramana Sharma, samjnaa-at-gmail-dot-com
#
# Use, modification and distribution are permitted subject to the
# "BSD-2-Clause"-type license stated in the accompanying file LICENSE.txt

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from labGraphCommon import *
from rgb2lab_int import *

class LabGraph2D(QWidget, HueOffsetInterface):

    def __init__(self, mainWindow, colorNotation, makeTableFn, fixedValName, var1Name, var1Min, var1Max, var2Name, var2Min, var2Max):

        assert var1Max > var1Min
        assert var2Max > var2Min

        QWidget.__init__(self)

        self.mainWindow = mainWindow
        self.colorNotation = colorNotation
        self.makeTableFn = makeTableFn
        self.fixedValName = fixedValName
        self.var1Name = var1Name
        self.var1Min = var1Min
        self.var1Max = var1Max
        self.var2Name = var2Name
        self.var2Min = var2Min
        self.var2Max = var2Max

        self.graphName = "{}{} for fixed {}".format(var1Name, var2Name, fixedValName)
        self.xSpan = var1Max - var1Min + 1
        self.ySpan = var2Max - var2Min + 1
        self.totalPoints = self.xSpan * self.ySpan
        self.xIsH = var1Name == "H"

        i = self.image = QImage(self.xSpan, self.ySpan, QImage.Format_ARGB32)
        i.setText("Software", "RGB2LAB GUI, © 2019, Shriramana Sharma; GPLv3; using Qt 5 via PyQt 5")
        i.setText("Disclaimer", "Although every effort is made to ensure accuracy, as per the terms of the GPLv3, no guarantee is provided.")

        t = self.redrawImageTimer = QTimer()
        t.setInterval(100)  # msecs
        t.timeout.connect(self.redrawImage)

        w = self.graph = GraphLabel(self, self.xSpan, self.ySpan)
        w.focusChanged.connect(self.graphFocusChanged)

        w = self.captionLabel = QLabel()
        w.setAlignment(Qt.AlignHCenter)

        l = self.mainLayout = QVBoxLayout()
        l.addWidget(self.graph, 0, Qt.AlignHCenter)
        l.addWidget(self.captionLabel, 0, Qt.AlignHCenter)
        self.setLayout(l)

        self.values = None

    def graphFocusChanged(self, x, y):
        self.values[self.var1Name] = self.applyHueOffset(self.var1Min + x, self.DATA_FROM_DISPLAY)
        self.values[self.var2Name] = self.var2Max - y
        self.mainWindow.writeSpins(self.colorNotation, [self.values[c] for c in self.colorNotation])

    def redrawIfNeeded(self):
        if self.values is None:  # initial draw
            self.values = self.mainWindow.labchValues.copy()
            self.redrawImage()
        else:
            prevFixedVal = self.values[self.fixedValName]
            self.values = self.mainWindow.labchValues.copy()
            if prevFixedVal == self.values[self.fixedValName]:
                self.redrawPixmap()  # no redrawImage
            else:
                self.redrawImageTimer.start()

    def redrawImage(self):
        self.redrawImageTimer.stop()
        fixedVal = self.values[self.fixedValName]
        table = self.makeTableFn(fixedVal)
        coverage = round(100 * table.inGamutCount / self.totalPoints, 2)
        axesText = "X: {} [{} to {}], Y: {} [{} to {}]".format(self.var1Name,
                                                               self.applyHueOffset(self.var1Min, self.DATA_FROM_DISPLAY),
                                                               self.applyHueOffset(self.var1Max, self.DATA_FROM_DISPLAY),
                                                               self.var2Name, self.var2Min, self.var2Max)
        self.captionLabel.setText("<b>{} = {}</b>; {}<br><b>{}%</b> of graph in gamut".format(
            self.fixedValName, fixedVal, axesText, coverage))
        titleText = "Graph showing sRGB gamut of {} colorspace {} representation 2D slice at {} = {}".format(
            self.mainWindow.colorSpaceName, "cylindrical" if self.colorNotation == "LCH" else "cartesian",
            self.fixedValName, fixedVal)
        st = self.image.setText
        st("Title", titleText)
        st("Description", titleText + "; Axes: {}; Coverage: {}% of graph in gamut; Parameters: D65 illuminant, 2 deg. observer".format(axesText, coverage))
        st("Creation Time", QDateTime.currentDateTime().toString(Qt.ISODate))
        for x in range(self.xSpan):
            xForDisplay = self.applyHueOffset(x, self.DISPLAY_FROM_DATA)
            for y in range(self.ySpan):
                rgb = table[x][y]
                self.image.setPixel(xForDisplay, self.ySpan - 1 - y, qRgb(rgb.r, rgb.g, rgb.b) if rgb.valid else Qt.transparent)
                # ySpan - 1 - y needed since we want y to increase upwards but in QImage it increases downwards
        self.redrawPixmap()

    def redrawPixmap(self):
        pixmap = QPixmap.fromImage(self.image)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        target = QPoint(self.applyHueOffset(self.values[self.var1Name] - self.var1Min, self.DISPLAY_FROM_DATA), self.var2Max - self.values[self.var2Name])
        painter.setPen(QColor(Qt.white))
        painter.drawEllipse(target, 11, 11)  # outer circle with inner plus
        for end in (QPoint(4, 0), QPoint(0, 4)):
            painter.drawLine(target, target - end)
            painter.drawLine(target, target + end)
        painter.setPen(QColor(Qt.black))  # inner circle with outer ticks
        painter.drawEllipse(target, 9, 9)
        for start, end in ((QPoint(9, 0), QPoint(5, 0)), (QPoint(0, 9), QPoint(0, 4))):
            painter.drawLine(target - start, target - end)
            painter.drawLine(target + start, target + end)
        painter.end()
        self.graph.setPixmap(pixmap)

class LabMultiGraph2D(QWidget):

    def __init__(self, mainWindow):

        QWidget.__init__(self)

        self.graph_ABforL = LabGraph2D(mainWindow, "LAB", makeTable_ABforL, "L", "A", -128, +128, "B", -128, +128)
        self.graph_BLforA = LabGraph2D(mainWindow, "LAB", makeTable_BLforA, "A", "B", -128, +128, "L",    0,  100)
        self.graph_ALforB = LabGraph2D(mainWindow, "LAB", makeTable_ALforB, "B", "A", -128, +128, "L",    0,  100)
        self.graph_HCforL = LabGraph2D(mainWindow, "LCH", makeTable_HCforL, "L", "H",    0,  359, "C",    0,  180)
        self.graph_HLforC = LabGraph2D(mainWindow, "LCH", makeTable_HLforC, "C", "H",    0,  359, "L",    0,  100)
        self.graph_CLforH = LabGraph2D(mainWindow, "LCH", makeTable_CLforH, "H", "C",    0,  180, "L",    0,  100)

        self.graphs = (self.graph_ABforL, self.graph_BLforA, self.graph_ALforB, self.graph_HCforL, self.graph_HLforC, self.graph_CLforH)

        l = self.mainLayout = QGridLayout()
        for i, graph in enumerate(self.graphs):
            l.addWidget(graph, i % 3, i // 3, Qt.AlignCenter)
        self.setLayout(l)

        t = self.rotateHueImageTimer = QTimer()
        t.setInterval(100)  # msecs
        t.timeout.connect(self.rotateHueImages)

    def updateGraphs(self):
        for g in self.graphs:
            g.redrawIfNeeded()

    def rotateHueImages(self):
        self.rotateHueImageTimer.stop()
        for g in self.graph_HCforL, self.graph_HLforC:
            g.redrawImage()  # slightly inefficient as recalculates data but easiest
