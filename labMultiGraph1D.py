# LabMultiGraph1D widget
# ======================
#
# visualize CIE LAB/LCH colorspaces
#
# Copyright (C) 2019, Shriramana Sharma, samjnaa-at-gmail-dot-com
#
# Use, modification and distribution are permitted subject to the
# "BSD-2-Clause"-type license stated in the accompanying file LICENSE.txt

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from rgb2lab_int import *

heightOfGraph1D = 30

class LabGraph1D(QWidget):

    def __init__(self, multiGraph, colorSpaceName, makeTableFn, fixed1Name, fixed2Name, varName, varMin, varMax):

        assert varMax > varMin

        QWidget.__init__(self, multiGraph)

        self.multiGraph = multiGraph
        self.colorSpaceName = colorSpaceName
        self.makeTableFn = makeTableFn
        self.fixed1Name = fixed1Name
        self.fixed2Name = fixed2Name
        self.varName = varName
        self.varMin = varMin
        self.varMax = varMax

        self.graphName = "{} for fixed {}{}".format(varName, fixed1Name, fixed2Name)
        self.varSpan = varMax - varMin + 1

        # for caption below and QImage metadata
        self.axisText = "X: {} [{} to {}]".format(varName, varMin, varMax)

        i = self.image = QImage(self.varSpan, heightOfGraph1D, QImage.Format_ARGB32)
        i.setText("Software", "RGB2LAB GUI, © 2019, Shriramana Sharma; GPLv3; using Qt 5 via PyQt 5")
        i.setText("Disclaimer", "Although every effort is made to ensure accuracy, as per the terms of the GPLv3, no guarantee is provided.")

        t = self.redrawImageTimer = QTimer()  # to delay redraw to avoid costly recalc while typing, fast spinning etc
        t.setInterval(100)  # msecs
        t.timeout.connect(self.redrawImage)

        w = self.graph = QLabel()
        w.setFixedSize(self.varSpan, heightOfGraph1D)
        w.setFrameShape(QFrame.Box)

        w = self.caption = QLabel()
        w.setAlignment(Qt.AlignHCenter)

        l = self.mainLayout = QVBoxLayout()
        l.addWidget(self.graph, 0, Qt.AlignHCenter)
        l.addWidget(self.caption, 0, Qt.AlignHCenter)
        self.setLayout(l)

        self.values = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pass
        elif event.button() == Qt.RightButton:
            fname = QFileDialog.getSaveFileName(self, "RGB2LAB GUI: Save “{}” graph".format(self.graphName), QDir.homePath(), "PNG images (*.png)")[0]
            if fname == "": return
            if not self.image.save(fname, "PNG"):
                QMessageBox.critical(self, "RGB2LAB GUI: Error", "Could not save the image to the chosen path. Perhaps the path is not writable. Please try again.")

    def redrawIfNeeded(self):
        if self.values is None:  # initial draw
            self.values = self.multiGraph.values.copy()
            self.redrawImage()
        elif self.values == self.multiGraph.values:
            return  # no redraw at all
        else:
            prevFixed1 = self.values[self.fixed1Name]
            prevFixed2 = self.values[self.fixed2Name]
            self.values = self.multiGraph.values.copy()
            if prevFixed1 == self.multiGraph.values[self.fixed1Name] and \
               prevFixed2 == self.multiGraph.values[self.fixed2Name]:
                self.redrawPixmap()  # no redrawImage
            else:
                self.redrawImageTimer.start()

    def redrawImage(self):
        self.redrawImageTimer.stop()
        fixed1 = self.values[self.fixed1Name]
        fixed2 = self.values[self.fixed2Name]
        table = self.makeTableFn(fixed1, fixed2)
        coverage = round(100 * table.inGamutCount / self.varSpan, 2)
        self.caption.setText("<b>{} = {}; {} = {}</b>; {}<br><b>{}%</b> of graph in gamut".format(
            self.fixed1Name, fixed1, self.fixed2Name, fixed2, self.axisText, coverage))
        titleText = "Graph showing sRGB representation of {} colorspace 1D slice at {} = {}, {} = {}".format(
            self.colorSpaceName, self.fixed1Name, fixed1, self.fixed2Name, fixed2)
        st = self.image.setText
        st("Title", titleText)
        st("Description", titleText + "; Axis: {}; Coverage: {}% of graph in gamut; Parameters: D65 illuminant, 2 deg. observer".format(self.axisText, coverage))
        st("Creation Time", QDateTime.currentDateTime().toString(Qt.ISODate))
        for var in range(self.varSpan):
            rgb = table[var]
            pix = qRgb(rgb.r, rgb.g, rgb.b) if rgb.valid else Qt.transparent
            for ht in range(heightOfGraph1D):
                self.image.setPixel(var, ht, pix)
        self.redrawPixmap()

    def redrawPixmap(self):
        pixmap = QPixmap.fromImage(self.image)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        target = QPoint(self.values[self.varName] - self.varMin, heightOfGraph1D // 2)
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
        self.setWindowTitle("RGB2LAB GUI: LAB/LCH Graphs")

        self.mainWindow = mainWindow

        self.graph_LforAB = LabGraph1D(self, "CIE LAB", makeTable_LforAB, "A", "B", "L",    0,  100)
        self.graph_AforBL = LabGraph1D(self, "CIE LAB", makeTable_AforBL, "B", "L", "A", -128, +128)
        self.graph_BforAL = LabGraph1D(self, "CIE LAB", makeTable_BforAL, "A", "L", "B", -128, +128)
        self.graph_LforHC = LabGraph1D(self, "CIE LCH", makeTable_LforHC, "H", "C", "L",    0,  100)
        self.graph_CforHL = LabGraph1D(self, "CIE LCH", makeTable_CforHL, "H", "L", "C",    0,  180)
        self.graph_HforCL = LabGraph1D(self, "CIE LCH", makeTable_HforCL, "C", "L", "H",    0,  359)

        self.graphs = (self.graph_LforAB, self.graph_AforBL, self.graph_BforAL, self.graph_LforHC, self.graph_CforHL, self.graph_HforCL)

        l = self.leftLayout = QVBoxLayout()
        l.addWidget(self.graph_LforAB)
        l.addWidget(self.graph_AforBL)
        l.addWidget(self.graph_BforAL)

        l = self.rightLayout = QVBoxLayout()
        l.addWidget(self.graph_LforHC)
        l.addWidget(self.graph_CforHL)
        l.addWidget(self.graph_HforCL)

        l = self.mainLayout = QHBoxLayout()
        l.addLayout(self.leftLayout)
        l.addLayout(self.rightLayout)
        self.setLayout(l)

    def setValues(self, lab, lch):
        self.values = dict(zip("LABLCH", lab + lch))  # doesn't matter that L will be overwritten once
        for g in self.graphs: g.redrawIfNeeded()
