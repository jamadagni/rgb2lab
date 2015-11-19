# LabDisplay widget
# =================
# visualize CIE LAB/LCH colorspaces
#
# Copyright (C) 2015, Shriramana Sharma
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rgb2lab_int import *

class LabGraph(QWidget):

    def __init__(self, labParent, colorSpaceName, makeTableFn, fixedValName, var1Name, var1Min, var1Max, var2Name, var2Min, var2Max):

        assert var1Max > var1Min
        assert var2Max > var2Min

        QWidget.__init__(self)

        self.labParent = labParent
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
        i.setText("Software", "RGB2LAB GUI, (C) 2015, Shriramana Sharma; GPLv3; using Qt 4 via PyQt 4")
        i.setText("Disclaimer", "Although every effort is made to ensure accuracy, as per the terms of the GPLv3, no guarantee is provided.")

        t = self.redrawImageTimer = QTimer() # to delay redraw to avoid costly recalc while typing, fast spinning etc
        t.setInterval(100) # msecs
        t.timeout.connect(self.redrawImage)

        w = self.graph = QLabel()
        w.setFixedSize(self.var1Span, self.var2Span)
        w.setFrameShape(QFrame.StyledPanel)

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
        coverage = round(100 * table.inGamutCount / self.totalPoints, 2)
        self.caption.setText("<b>{} = {}</b>; {}<br><b>{}%</b> of graph in gamut".format(self.fixedValName, fixedVal, self.axesText, coverage))
        titleText = "Graph showing sRGB representation of {} colorspace slice at {} = {}".format(self.colorSpaceName, self.fixedValName, fixedVal)
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
        self.setWindowTitle("RGB2LAB GUI: LAB/LCH Graphs")

        self.mainWindow = mainWindow

        self.graphL_AB = LabGraph(self, "CIE LAB", makeTableL_AB, "L", "A", -128, +128, "B", -128, +128)
        self.graphA_BL = LabGraph(self, "CIE LAB", makeTableA_BL, "A", "B", -128, +128, "L",    0,  100)
        self.graphB_AL = LabGraph(self, "CIE LAB", makeTableB_AL, "B", "A", -128, +128, "L",    0,  100)
        self.graphL_HC = LabGraph(self, "CIE LCH", makeTableL_HC, "L", "H",    0,  359, "C",    0,  180)
        self.graphC_HL = LabGraph(self, "CIE LCH", makeTableC_HL, "C", "H",    0,  359, "L",    0,  100)
        self.graphH_CL = LabGraph(self, "CIE LCH", makeTableH_CL, "H", "C",    0,  180, "L",    0,  100)

        self.graphs = (self.graphL_AB, self.graphA_BL, self.graphB_AL, self.graphL_HC, self.graphC_HL, self.graphH_CL)
        self.graphNames = ("L (AB)", "A", "B", "L (CH)", "C", "H") # order must correspond to above

        self.saveImageRadios = tuple(QRadioButton("Fixed &" + name) for name in self.graphNames)
        self.saveImageRadios[0].setChecked(True)
        self.saveImageButton = QPushButton("&Save as...")

        l = self.saveImageGrid = QGridLayout()
        for col in range(2):
            for row in range(3):
                l.addWidget(self.saveImageRadios[col * 3 + row], row, col)
        l.addWidget(self.saveImageButton, 0, 2, 3, 1)

        w = self.saveImageFrame = QFrame()
        w.setFrameShape(QFrame.StyledPanel)
        w.setLayout(self.saveImageGrid)

        l = self.leftLayout = QVBoxLayout()
        l.addWidget(self.graphL_AB)
        l.addWidget(self.graphA_BL)
        l.addWidget(self.graphB_AL)

        l = self.rightLayout = QVBoxLayout()
        l.addWidget(self.graphL_HC)
        l.addWidget(self.graphC_HL)
        l.addWidget(self.graphH_CL)
        l.addWidget(self.saveImageFrame)

        l = self.mainLayout = QHBoxLayout()
        l.addLayout(self.leftLayout)
        l.addLayout(self.rightLayout)
        self.setLayout(l)

        self.saveImageButton.clicked.connect(self.saveImage)

        self.values = None
        self.isShown = False

    def closeEvent(self, event):
        self.mainWindow.showGraphsCheckBox.setChecked(False)

    def showEvent(self, event):
        self.isShown = True
        self.redraw()

    def hideEvent(self, event):
        self.isShown = False

    def setValues(self, lab, lch):
        self.values = dict(zip("LABLCH", lab + lch)) # doesn't matter that L will be overwritten once
        if self.isShown: self.redraw()

    def redraw(self):
        for g in self.graphs: g.redrawIfNeeded()

    def saveImage(self):
        for graphName, graph, saveImageRadio in zip(self.graphNames, self.graphs, self.saveImageRadios):
            if saveImageRadio.isChecked(): break
        fname = QFileDialog.getSaveFileName(self, "RGB2LAB GUI: Save {} graph".format(graphName), QDir.homePath(), "PNG images (*.png)")
        if fname == "": return
        if not graph.image.save(fname, "PNG"):
            QMessageBox.critical(self, "RGB2LAB GUI: Error", "Could not save the image to the chosen path. Perhaps the location is not writable. Please try again.")
