#! /usr/bin/env python3

# RGB2LAB GUI
# ===========
#
# - convert color values from RGB to/from CIELAB color space
#   for sRGB gamut, D65 illuminant, 2° observer
# - Visualize the color space in cartesian and cylindrical representations
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

class InvalidInputError(RuntimeError):
    pass  # separate class for identification

class MainWindow(QWidget):

    def __init__(self):

        QWidget.__init__(self)
        self.setWindowTitle("RGB2LAB GUI")

        self.colorSpaceName = "CIELAB"

        w = self.parameterLabel = QLabel("sRGB gamut, D65 illuminant, 2° observer")
        w.setAlignment(Qt.AlignHCenter)

        w = self.graphClickLabel = QLabel("Left-click on any graph to move the focus, right-click to save")
        w.setAlignment(Qt.AlignHCenter)

        l = self.hueOffsetLabel = QLabel("Hue &offset:")
        w = self.hueOffsetSlider = QSlider(Qt.Horizontal)
        w.setRange(0, 359)
        l.setBuddy(w)

        l = self.rgbHexLabel = QLabel("<font color='green'>He&x</font>:")
        w = self.rgbHexInput = QLineEdit()
        w.setInputMask("HHHHHH")
        w.setPlaceholderText("out of gamut")
        l.setBuddy(w)

        def colorLabels(chars):
            return [QLabel("<font color='green'>&" + c + "</font>:") for c in chars]
        def plainLabels(chars):
            return [QLabel("&" + c + ":") for c in chars]

        self.colorNotationTypes = ("RGB", "LAB", "LCH")
        self.updateFromFunctions = (self.updateFromRgb, self.updateFromLab, self.updateFromLch)
        self.spinLabels = colorLabels("RGB") + plainLabels("LAB") + colorLabels("LCH")

        self.spinBoxes = [QSpinBox() for l in self.spinLabels]
        for label, box in zip(self.spinLabels, self.spinBoxes):
            label.setBuddy(box)

        for box, maxVal in zip(self.spinBoxes, (255, 255, 255, 100, 128, 128, 100, 180, 359)):
            box.setMaximum(maxVal)
        for i in 4, 5:  # a and b positions
            self.spinBoxes[i].setMinimum(-128)
        for box in self.spinBoxes[:3]:  # RGB positions
            box.setMinimum(-1)
            box.setSpecialValueText("oog")
        box = self.spinBoxes[-1]  # H position
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
        l.addWidget(self.parameterLabel)
        l.addSpacing(heightOfGraph1D)
        l.addLayout(self.inputGrid)

        l = self.layout2 = QHBoxLayout()
        l.addLayout(self.layout1)
        l.addSpacing(heightOfGraph1D)
        l.addWidget(self.colorDisplay)

        l = self.layout3 = QHBoxLayout()
        l.addWidget(self.hueOffsetLabel)
        l.addWidget(self.hueOffsetSlider)

        l = self.leftLayout = QVBoxLayout()
        l.addStretch()
        l.addLayout(self.layout2)
        l.addSpacing(heightOfGraph1D)
        l.addLayout(self.layout3)
        l.addStretch()
        l.addWidget(self.graphClickLabel)
        l.addStretch()
        l.addWidget(self.labMultiGraph1D)
        l.addStretch()

        l = self.mainLayout = QHBoxLayout()
        l.addLayout(self.leftLayout)
        l.addWidget(self.labMultiGraph2D)
        self.setLayout(l)

        self.makeColorConnections()
        for multiGraph in self.labMultiGraph1D, self.labMultiGraph2D:
            self.hueOffsetSlider.valueChanged.connect(multiGraph.rotateHueImageTimer.start)

        self.lastImageSaveDir = QDir.homePath()
        self.rgbHexInput.setText("45aa45")

    def makeColorConnections(self):
        self.rgbHexInput.textChanged.connect(self.updateFromRgb)
        for i, box in enumerate(self.spinBoxes):
            box.valueChanged.connect(self.updateFromFunctions[i // 3])

    def breakColorConnections(self):
        self.rgbHexInput.textChanged.disconnect()
        for b in self.spinBoxes:
            b.valueChanged.disconnect()

    def changeLabelColor(self, start, toColor):
        fromColor = "green" if toColor == "red" else "red"
        seq = self.spinLabels[start : start + 3] if type(start) is int else (start, )
        for l in seq:
            l.setText(l.text().replace(fromColor, toColor))

    def writeRgbText(self, rgb):
        self.changeLabelColor(self.rgbHexLabel, "green")
        self.rgbHexInput.setText("" if -1 in rgb else "".join(hex(c)[2:].zfill(2) for c in rgb))

    def writeSpins(self, colorNotation, vals):
        start = self.colorNotationTypes.index(colorNotation) * 3
        for i in range(3):
            if colorNotation in ("RGB", "LCH"):
                self.changeLabelColor(self.spinLabels[start + i], "green")
            self.spinBoxes[start + i].setValue(vals[i])

    def readSpins(self, colorNotation):
        start = self.colorNotationTypes.index(colorNotation) * 3
        x, y, z = map(QSpinBox.value, self.spinBoxes[start : start + 3])
        # handle invalid input values
        if colorNotation == "RGB":
            if -1 in (x, y, z):
                self.changeLabelColor(start, "red")
                raise InvalidInputError
            else:
                self.changeLabelColor(start, "green")
        elif colorNotation == "LCH":
            if z == -1 and y != 0:
                self.changeLabelColor(start, "red")
                raise InvalidInputError
            else:
                self.changeLabelColor(start, "green")
        return x, y, z

    def updateLabchGraphs(self, lab, lch):
        self.labchValues = dict(zip("LABLCH", lab + lch))  # doesn't matter that L will be overwritten once
        self.labMultiGraph1D.updateGraphs()
        self.labMultiGraph2D.updateGraphs()

    def updateFromRgb(self, rgbInput):
        if type(rgbInput) is str:  # signal came from rgbHexInput
            if len(rgbInput) != 6:  # don't compute until full rgb code is input
                self.changeLabelColor(self.rgbHexLabel, "red")
                return
            else:
                self.changeLabelColor(self.rgbHexLabel, "green")
                rgb = tuple(int(rgbInput[i * 2 : i * 2 + 2], 16) for i in range(3))
        else:  # signal came from one of the RGB spins
            try:
                rgb = self.readSpins("RGB")
            except InvalidInputError:
                return  # don't compute
        lab, lch = labLchFromRgbInt(rgb)
        self.breakColorConnections()
        if type(rgbInput) is str:
            self.writeSpins("RGB", rgb)
        else:
            self.writeRgbText(rgb)
        self.writeSpins("LCH", lch)
        self.writeSpins("LAB", lab)
        self.updateColor()
        self.makeColorConnections()
        self.updateLabchGraphs(lab, lch)

    def updateFromLab(self):
        try:
            lab = self.readSpins("LAB")
        except InvalidInputError:
            return  # don't compute
        rgb, lch = rgbLchFromLabInt(lab)
        self.breakColorConnections()
        self.writeRgbText(rgb)
        self.writeSpins("RGB", rgb)
        self.writeSpins("LCH", lch)
        self.updateColor()
        self.makeColorConnections()
        self.updateLabchGraphs(lab, lch)

    def updateFromLch(self):
        try:
            lch = self.readSpins("LCH")
        except InvalidInputError:
            return  # don't compute
        rgb, lab = rgbLabFromLchInt(lch)
        self.breakColorConnections()
        self.writeRgbText(rgb)
        self.writeSpins("RGB", rgb)
        self.writeSpins("LAB", lab)
        self.updateColor()
        self.makeColorConnections()
        self.updateLabchGraphs(lab, lch)

    def updateColor(self):
        self.colorDisplay.setColor(QColor(Qt.transparent) if self.rgbHexInput.text() == "" else QColor.fromRgb(*self.readSpins("RGB")))

app = QApplication([])
app.setWindowIcon(QIcon("rgb2lab.png"))
mainWindow = MainWindow()
mainWindow.show()
app.exec_()
