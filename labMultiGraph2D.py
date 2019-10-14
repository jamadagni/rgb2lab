# LabMultiGraph2D widget
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

class LabGraph2D(QWidget):

    def __init__(self, multiGraph, colorSpaceName, makeTableFn, fixedValName, var1Name, var1Min, var1Max, var2Name, var2Min, var2Max):

        assert var1Max > var1Min
        assert var2Max > var2Min

        QWidget.__init__(self, multiGraph)

        self.multiGraph = multiGraph
        self.colorSpaceName = colorSpaceName
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

        # for caption below and QImage metadata
        self.axesText = "X: {} [{} to {}], Y: {} [{} to {}]".format(var1Name, var1Min, var1Max, var2Name, var2Min, var2Max)

        i = self.image = QImage(self.var1Span, self.var2Span, QImage.Format_ARGB32)
        i.setText("Software", "RGB2LAB GUI, © 2019, Shriramana Sharma; GPLv3; using Qt 5 via PyQt 5")
        i.setText("Disclaimer", "Although every effort is made to ensure accuracy, as per the terms of the GPLv3, no guarantee is provided.")

        t = self.redrawImageTimer = QTimer()  # to delay redraw to avoid costly recalc while typing, fast spinning etc
        t.setInterval(100)  # msecs
        t.timeout.connect(self.redrawImage)

        w = self.graph = QLabel()
        w.setFixedSize(self.var1Span, self.var2Span)
        w.setFrameShape(QFrame.Box)

        w = self.caption = QLabel()
        w.setAlignment(Qt.AlignHCenter)

        l = self.mainLayout = QVBoxLayout()
        l.addWidget(self.graph, 0, Qt.AlignHCenter)
        l.addWidget(self.caption, 0, Qt.AlignHCenter)
        self.setLayout(l)

        self.values = None

    def redrawIfNeeded(self):
        if self.values is None:  # initial draw
            self.values = self.multiGraph.values.copy()
            self.redrawImage()
        elif self.values == self.multiGraph.values:
            return  # no redraw at all
        else:
            prevFixedVal = self.values[self.fixedValName]
            self.values = self.multiGraph.values.copy()
            if prevFixedVal == self.multiGraph.values[self.fixedValName]:
                self.redrawPixmap()  # no redrawImage
            else:
                self.redrawImageTimer.start()

    def redrawImage(self):
        self.redrawImageTimer.stop()
        fixedVal = self.values[self.fixedValName]
        table = self.makeTableFn(fixedVal)
        coverage = round(100 * table.inGamutCount / self.totalPoints, 2)
        self.caption.setText("<b>{} = {}</b>; {}<br><b>{}%</b> of graph in gamut".format(
            self.fixedValName, fixedVal, self.axesText, coverage))
        titleText = "Graph showing sRGB representation of {} colorspace 2D slice at {} = {}".format(
            self.colorSpaceName, self.fixedValName, fixedVal)
        st = self.image.setText
        st("Title", titleText)
        st("Description", titleText + "\nAxes: {}\nCoverage: {}% of graph in gamut\nParameters: D65 illuminant, 2 deg. observer".format(self.axesText, coverage))
        st("Creation Time", QDateTime.currentDateTime().toString(Qt.ISODate))
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
        self.setWindowTitle("RGB2LAB GUI: LAB/LCH Graphs")

        self.mainWindow = mainWindow

        self.graph_ABforL = LabGraph2D(self, "CIE LAB", makeTable_ABforL, "L", "A", -128, +128, "B", -128, +128)
        self.graph_BLforA = LabGraph2D(self, "CIE LAB", makeTable_BLforA, "A", "B", -128, +128, "L",    0,  100)
        self.graph_ALforB = LabGraph2D(self, "CIE LAB", makeTable_ALforB, "B", "A", -128, +128, "L",    0,  100)
        self.graph_HCforL = LabGraph2D(self, "CIE LCH", makeTable_HCforL, "L", "H",    0,  359, "C",    0,  180)
        self.graph_HLforC = LabGraph2D(self, "CIE LCH", makeTable_HLforC, "C", "H",    0,  359, "L",    0,  100)
        self.graph_CLforH = LabGraph2D(self, "CIE LCH", makeTable_CLforH, "H", "C",    0,  180, "L",    0,  100)

        self.graphs = (self.graph_ABforL, self.graph_BLforA, self.graph_ALforB, self.graph_HCforL, self.graph_HLforC, self.graph_CLforH)
        self.graphNames = ("L (AB)", "A", "B", "L (CH)", "C", "H")  # order must correspond to above

        self.saveImageLabel = QLabel("Fixed:")
        self.saveImageRadios = tuple(QRadioButton("&" + name) for name in self.graphNames)
        self.saveImageRadios[0].setChecked(True)
        self.saveImageButton = QPushButton("&Save as...")

        l = self.saveImageLayout = QHBoxLayout()
        l.addWidget(self.saveImageLabel)
        for w in self.saveImageRadios:
            l.addWidget(w)
        l.addWidget(self.saveImageButton)

        w = self.saveImageFrame = QFrame()
        w.setFrameShape(QFrame.StyledPanel)
        w.setLayout(self.saveImageLayout)

        l = self.leftLayout = QVBoxLayout()
        l.addWidget(self.graph_ABforL)
        l.addWidget(self.graph_BLforA)
        l.addWidget(self.graph_ALforB)

        l = self.rightLayout = QVBoxLayout()
        l.addWidget(self.graph_HCforL)
        l.addWidget(self.graph_HLforC)
        l.addWidget(self.graph_CLforH)

        l = self.upperLayout = QHBoxLayout()
        l.addLayout(self.leftLayout)
        l.addLayout(self.rightLayout)

        l = self.mainLayout = QVBoxLayout()
        l.addLayout(self.upperLayout)
        l.addWidget(self.saveImageFrame)
        self.setLayout(l)

        self.saveImageButton.clicked.connect(self.saveImage)

    def setValues(self, lab, lch):
        self.values = dict(zip("LABLCH", lab + lch))  # doesn't matter that L will be overwritten once
        for g in self.graphs: g.redrawIfNeeded()

    def saveImage(self):
        for graphName, graph, saveImageRadio in zip(self.graphNames, self.graphs, self.saveImageRadios):
            if saveImageRadio.isChecked(): break
        fname = QFileDialog.getSaveFileName(self, "RGB2LAB GUI: Save {} graph".format(graphName), QDir.homePath(), "PNG images (*.png)")
        if fname == "": return
        if not graph.image.save(fname, "PNG"):
            QMessageBox.critical(self, "RGB2LAB GUI: Error", "Could not save the image to the chosen path. Perhaps the location is not writable. Please try again.")
