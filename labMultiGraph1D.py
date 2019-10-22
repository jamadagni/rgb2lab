# LabMultiGraph1D widget
# ======================
#
# visualize 1D slices of the CIELAB color space
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

heightOfGraph1D = 30

class LabGraph1D(QWidget, HueOffsetInterface):

    def __init__(self, mainWindow, colorNotation, makeTableFn, fixed1Name, fixed2Name, varName, varMin, varMax):

        assert varMax > varMin

        QWidget.__init__(self)

        self.mainWindow = mainWindow
        self.colorNotation = colorNotation
        self.makeTableFn = makeTableFn
        self.fixed1Name = fixed1Name
        self.fixed2Name = fixed2Name
        self.varName = varName
        self.varMin = varMin
        self.varMax = varMax

        self.graphName = "{} for fixed {}{}".format(varName, fixed1Name, fixed2Name)
        self.xSpan = varMax - varMin + 1
        self.xIsH = varName == "H"

        i = self.image = QImage(self.xSpan, heightOfGraph1D, QImage.Format_ARGB32)
        i.setText("Software", "RGB2LAB GUI, © 2019, Shriramana Sharma; GPLv3; using Qt 5 via PyQt 5")
        i.setText("Disclaimer", "Although every effort is made to ensure accuracy, as per the terms of the GPLv3, no guarantee is provided.")

        t = self.redrawImageTimer = QTimer()
        t.setInterval(100)  # msecs
        t.timeout.connect(self.redrawImage)

        w = self.graph = GraphLabel(self, self.xSpan, heightOfGraph1D)
        w.focusChanged.connect(self.graphFocusChanged)

        w = self.captionLabel = QLabel()
        w.setAlignment(Qt.AlignHCenter)

        l = self.mainLayout = QVBoxLayout()
        l.addWidget(self.graph, 0, Qt.AlignHCenter)
        l.addWidget(self.captionLabel, 0, Qt.AlignHCenter)
        self.setLayout(l)

        self.values = None

    def graphFocusChanged(self, x, y):
        self.values[self.varName] = self.applyHueOffset(self.varMin + x, self.DATA_FROM_DISPLAY)
        self.mainWindow.writeSpins(self.colorNotation, [self.values[c] for c in self.colorNotation])

    def redrawIfNeeded(self):
        if self.values is None:  # initial draw
            self.values = self.mainWindow.labchValues.copy()
            self.redrawImage()
        else:
            prevFixed1 = self.values[self.fixed1Name]
            prevFixed2 = self.values[self.fixed2Name]
            self.values = self.mainWindow.labchValues.copy()
            if prevFixed1 == self.values[self.fixed1Name] and \
               prevFixed2 == self.values[self.fixed2Name]:
                self.redrawPixmap()  # no redrawImage
            else:
                self.redrawImageTimer.start()

    def redrawImage(self):
        self.redrawImageTimer.stop()
        fixed1 = self.values[self.fixed1Name]
        fixed2 = self.values[self.fixed2Name]
        table = self.makeTableFn(fixed1, fixed2)
        coverage = round(100 * table.inGamutCount / self.xSpan, 2)
        axisText = "X: {} [{} to {}]".format(self.varName,
                                             self.applyHueOffset(self.varMin, self.DATA_FROM_DISPLAY),
                                             self.applyHueOffset(self.varMax, self.DATA_FROM_DISPLAY))
        self.captionLabel.setText("<b>{} = {}; {} = {}</b>; {}<br><b>{}%</b> of graph in gamut".format(
            self.fixed1Name, fixed1, self.fixed2Name, fixed2, axisText, coverage))
        titleText = "Graph showing sRGB gamut of {} colorspace {} representation 1D slice at {} = {}, {} = {}".format(
            self.mainWindow.colorSpaceName, "cylindrical" if self.colorNotation == "LCH" else "cartesian",
            self.fixed1Name, fixed1, self.fixed2Name, fixed2)
        st = self.image.setText
        st("Title", titleText)
        st("Description", titleText + "; Axis: {}; Coverage: {}% of graph in gamut; Parameters: D65 illuminant, 2 deg. observer".format(axisText, coverage))
        st("Creation Time", QDateTime.currentDateTime().toString(Qt.ISODate))
        for x in range(self.xSpan):
            rgb = table[x]
            pix = qRgb(rgb.r, rgb.g, rgb.b) if rgb.valid else Qt.transparent
            xForDisplay = self.applyHueOffset(x, self.DISPLAY_FROM_DATA)
            for y in range(heightOfGraph1D):
                self.image.setPixel(xForDisplay, y, pix)
        self.redrawPixmap()

    def redrawPixmap(self):
        pixmap = QPixmap.fromImage(self.image)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        target = QPoint(self.applyHueOffset(self.values[self.varName] - self.varMin, self.DISPLAY_FROM_DATA), heightOfGraph1D // 2)
        painter.setPen(QColor(Qt.white))  # inner ticks
        off = QPoint(0, 4)
        painter.drawLine(target, target - off)
        painter.drawLine(target, target + off)
        painter.setPen(QColor(Qt.black))  # outer ticks
        start, end = QPoint(0, 9), QPoint(0, 4)
        painter.drawLine(target - start, target - end)
        painter.drawLine(target + start, target + end)
        painter.end()
        self.graph.setPixmap(pixmap)

class LabMultiGraph1D(QWidget):

    def __init__(self, mainWindow):

        QWidget.__init__(self)

        self.graph_LforAB = LabGraph1D(mainWindow, "LAB", makeTable_LforAB, "A", "B", "L",    0,  100)
        self.graph_AforBL = LabGraph1D(mainWindow, "LAB", makeTable_AforBL, "B", "L", "A", -128, +128)
        self.graph_BforAL = LabGraph1D(mainWindow, "LAB", makeTable_BforAL, "A", "L", "B", -128, +128)
        self.graph_LforHC = LabGraph1D(mainWindow, "LCH", makeTable_LforHC, "H", "C", "L",    0,  100)
        self.graph_CforHL = LabGraph1D(mainWindow, "LCH", makeTable_CforHL, "H", "L", "C",    0,  180)
        self.graph_HforCL = LabGraph1D(mainWindow, "LCH", makeTable_HforCL, "C", "L", "H",    0,  359)

        self.graphs = (self.graph_LforAB, self.graph_AforBL, self.graph_BforAL, self.graph_LforHC, self.graph_CforHL, self.graph_HforCL)

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
        self.graph_HforCL.redrawImage()  # slightly inefficient as recalculates data but easiest
