#! /usr/bin/env python3

# RGB2LAB GUI
# ===========
#
# - convert color values from RGB to/from CIE LAB/LCH
#   for sRGB gamut, D65 illuminant, 2° observer
# - visualize CIE LAB and CIE LCH colorspaces
#
# Copyright (C) 2019, Shriramana Sharma, samjnaa-at-gmail-dot-com
#
# Use, modification and distribution are permitted subject to the
# "BSD-2-Clause"-type license stated in the accompanying file LICENSE.txt

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from rgb2lab_int import *
from colorDisplay import *
from labMultiGraph1D import *
from labMultiGraph2D import *

class InvalidInputError(RuntimeError): pass # separate class for identification

class MainWindow(QWidget):

    def __init__(self):

        QWidget.__init__(self)
        self.setWindowTitle("RGB2LAB GUI")

        w = self.parameters = QLabel("sRGB gamut, D65 illuminant, 2° observer")
        w.setAlignment(Qt.AlignHCenter)

        w = self.graphClickLabel = QLabel("Left-click on any graph to move the focus, right-click to save")
        w.setAlignment(Qt.AlignHCenter)

        label = self.rgbHexLabel = QLabel("<font color='green'>He&x</font>:")
        edit = self.rgbHexInput = QLineEdit()
        edit.setInputMask("HHHHHH")
        edit.setPlaceholderText("out of gamut")
        label.setBuddy(edit)

        def colorLabels(chars): return [QLabel("<font color='green'>&" + c + "</font>:") for c in chars]
        def plainLabels(chars): return [QLabel("&" + c + ":") for c in chars]

        self.systemOrder = ("RGB", "Lab", "LCh")
        self.updateFromFnSeq = (self.updateFromRgb, self.updateFromLab, self.updateFromLch)
        self.spinLabels = colorLabels("RGB") + plainLabels("Lab") + colorLabels("LCh")

        self.spinBoxes = [QSpinBox() for l in self.spinLabels]
        for label, box in zip(self.spinLabels, self.spinBoxes):
            label.setBuddy(box)

        for box, maxVal in zip(self.spinBoxes, (255, 255, 255, 100, 128, 128, 100, 180, 359)):
            box.setMaximum(maxVal)
        for i in 4, 5: # a and b positions
            self.spinBoxes[i].setMinimum(-128)
        for box in self.spinBoxes[:3]: # RGB positions
            box.setMinimum(-1)
            box.setSpecialValueText("oog")
        box = self.spinBoxes[-1] # h position
        box.setMinimum(-1)
        box.setSpecialValueText("nil")
        box.setWrapping(True)

        l = self.inputGrid = QGridLayout()
        l.addWidget(self.rgbHexLabel, 0, 0)
        l.addWidget(self.rgbHexInput, 0, 1, 1, 5)
        for r in range(len(self.spinBoxes) // 3):
            for c in range(3):
                i = r * 3 + c
                l.addWidget(self.spinLabels[i], r + 1, c * 2)
                l.addWidget(self.spinBoxes[i], r + 1, c * 2 + 1)

        self.colorDisplay = ColorDisplay()
        self.labMultiGraph1D = LabMultiGraph1D(self)
        self.labMultiGraph2D = LabMultiGraph2D(self)

        l = self.layout1 = QVBoxLayout()
        l.addWidget(self.parameters)
        l.addSpacing(heightOfGraph1D)
        l.addLayout(self.inputGrid)

        l = self.layout2 = QHBoxLayout()
        l.addLayout(self.layout1)
        l.addSpacing(heightOfGraph1D)
        l.addWidget(self.colorDisplay)

        l = self.leftLayout = QVBoxLayout()
        l.addStretch()
        l.addLayout(self.layout2)
        l.addSpacing(heightOfGraph1D)
        l.addWidget(self.graphClickLabel)
        l.addStretch()
        l.addWidget(self.labMultiGraph1D)
        l.addStretch()

        l = self.mainLayout = QHBoxLayout()
        l.addLayout(self.leftLayout)
        l.addWidget(self.labMultiGraph2D)
        self.setLayout(l)

        self.makeColorConnections()
        #for slot in self.labMultiGraph1D.setVisible, self.labMultiGraph2D.setVisible, self.activateWindow, self.raise_, self.rgbHexInput.setFocus:
            #self.showGraphsCheckBox.clicked.connect(slot)

        self.rgbHexInput.setText("45aa45")

    #def closeEvent(self, event):
        #self.labMultiGraph1D.close()
        #self.labMultiGraph2D.close()

    def makeColorConnections(self):
        self.rgbHexInput.textChanged.connect(self.updateFromRgb)
        for i, box in enumerate(self.spinBoxes):
            box.valueChanged.connect(self.updateFromFnSeq[i // 3])

    def breakColorConnections(self):
        self.rgbHexInput.textChanged.disconnect()
        for b in self.spinBoxes: b.valueChanged.disconnect()

    def changeLabelColor(self, start, toColor):
        fromColor = "green" if toColor == "red" else "red"
        seq = self.spinLabels[start : start + 3] if type(start) is int else (start, )
        for l in seq:
            l.setText(l.text().replace(fromColor, toColor))

    def writeRgbText(self, rgb):
        self.changeLabelColor(self.rgbHexLabel, "green")
        self.rgbHexInput.setText("" if -1 in rgb else "".join(hex(c)[2:].zfill(2) for c in rgb))

    def writeSpins(self, colorSystem, vals):
        start = self.systemOrder.index(colorSystem) * 3
        for i in range(3):
            if colorSystem in ("RGB", "LCh"): self.changeLabelColor(self.spinLabels[start + i], "green")
            self.spinBoxes[start + i].setValue(vals[i])

    def readSpins(self, colorSystem):
        start = self.systemOrder.index(colorSystem) * 3
        x, y, z = map(QSpinBox.value, self.spinBoxes[start : start + 3])
        # handle invalid input values
        if colorSystem == "RGB":
            if -1 in (x, y, z):
                self.changeLabelColor(start, "red")
                raise InvalidInputError
            else:
                self.changeLabelColor(start, "green")
        elif colorSystem == "LCh":
            if z == -1 and y != 0:
                self.changeLabelColor(start, "red")
                raise InvalidInputError
            else:
                self.changeLabelColor(start, "green")
        return x, y, z

    def updateFromRgb(self, rgbInput):
        if type(rgbInput) is str: # signal came from rgbHexInput
            if len(rgbInput) != 6: # don't compute until full rgb code is input
                self.changeLabelColor(self.rgbHexLabel, "red")
                return
            else:
                self.changeLabelColor(self.rgbHexLabel, "green")
                rgb = tuple(int(rgbInput[i * 2 : i * 2 + 2], 16) for i in range(3))
        else: # signal came from one of the RGB spins
            try:
                rgb = self.readSpins("RGB")
            except InvalidInputError:
                return # don't compute
        lab, lch = labLchFromRgbInt(rgb)
        self.labMultiGraph1D.setValues(lab, lch)
        self.labMultiGraph2D.setValues(lab, lch)
        self.breakColorConnections()
        if type(rgbInput) is str:
            self.writeSpins("RGB", rgb)
        else:
            self.writeRgbText(rgb)
        self.writeSpins("LCh", lch)
        self.writeSpins("Lab", lab)
        self.updateColor()
        self.makeColorConnections()

    def updateFromLab(self):
        try:
            lab = self.readSpins("Lab")
        except InvalidInputError:
            return # don't compute
        rgb, lch = rgbLchFromLabInt(lab)
        self.labMultiGraph1D.setValues(lab, lch)
        self.labMultiGraph2D.setValues(lab, lch)
        self.breakColorConnections()
        self.writeRgbText(rgb)
        self.writeSpins("RGB", rgb)
        self.writeSpins("LCh", lch)
        self.updateColor()
        self.makeColorConnections()

    def updateFromLch(self):
        try:
            lch = self.readSpins("LCh")
        except InvalidInputError:
            return # don't compute
        rgb, lab = rgbLabFromLchInt(lch)
        self.labMultiGraph1D.setValues(lab, lch)
        self.labMultiGraph2D.setValues(lab, lch)
        self.breakColorConnections()
        self.writeRgbText(rgb)
        self.writeSpins("RGB", rgb)
        self.writeSpins("Lab", lab)
        self.updateColor()
        self.makeColorConnections()

    def updateColor(self):
        self.colorDisplay.setColor(QColor(Qt.transparent) if self.rgbHexInput.text() == "" else QColor.fromRgb(*self.readSpins("RGB")))

app = QApplication([])
app.setWindowIcon(QIcon("rgb2lab.png"))
mainWindow = MainWindow()
mainWindow.show()
app.exec_()
