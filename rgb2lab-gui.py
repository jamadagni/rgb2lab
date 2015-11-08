#! /usr/bin/env python3

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rgb2lab_int import *
from colorDisplay import *
from labDisplay import *

class InvalidInputError(RuntimeError): pass # separate class for identification

class MainWindow(QWidget):

    def __init__(self):

        QWidget.__init__(self)
        self.setWindowTitle("RGB2LAB GUI")

        w = self.parameters = QLabel("sRGB gamut, D65 illuminant, 2° observer")
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

        l = self.grid = QGridLayout()
        l.addWidget(self.rgbHexLabel, 0, 0)
        l.addWidget(self.rgbHexInput, 0, 1, 1, 5)
        for r in range(len(self.spinBoxes) // 3):
            for c in range(3):
                i = r * 3 + c
                l.addWidget(self.spinLabels[i], r + 1, c * 2)
                l.addWidget(self.spinBoxes[i], r + 1, c * 2 + 1)

        self.showGraphsCheckBox = QCheckBox("&Show Lab graphs")
        self.colorDisplay = ColorDisplay()

        l = QVBoxLayout()
        l.addWidget(self.parameters)
        l.addLayout(self.grid)
        l.addWidget(self.colorDisplay)
        l.addWidget(self.showGraphsCheckBox)
        self.setLayout(l)

        self.labDisplay = LabDisplay(self)

        self.makeColorConnections()
        for slot in self.labDisplay.setVisible, self.activateWindow, self.raise_, self.rgbHexInput.setFocus:
            self.showGraphsCheckBox.clicked.connect(slot)
        self.rgbHexInput.setText("ababab")

    def closeEvent(self, event):
        self.labDisplay.close()

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

    def writeRgbText(self, r, g, b):
        self.changeLabelColor(self.rgbHexLabel, "green")
        self.rgbHexInput.setText("" if -1 in (r, g, b) else "".join(hex(c)[2:].zfill(2) for c in (r, g, b)))

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

    def updateFromRgb(self, rgb):
        if type(rgb) is str: # signal came from rgbHexInput
            if len(rgb) != 6: # don't compute until full rgb code is input
                self.changeLabelColor(self.rgbHexLabel, "red")
                return
            else:
                self.changeLabelColor(self.rgbHexLabel, "green")
                r, g, b = (int(rgb[i * 2 : i * 2 + 2], 16) for i in range(3))
        else: # signal came from one of the RGB spins
            try:
                r, g, b = self.readSpins("RGB")
            except InvalidInputError:
                return # don't compute
        L, A, B, l, c, h = labLchFromRgbInt(r, g, b)
        self.labDisplay.setValues(L, A, B, c, h)
        self.breakColorConnections()
        if type(rgb) is str:
            self.writeSpins("RGB", (r, g, b))
        else:
            self.writeRgbText(r, g, b)
        self.writeSpins("LCh", (l, c, h))
        self.writeSpins("Lab", (L, A, B))
        self.updateColor()
        self.makeColorConnections()

    def updateFromLab(self):
        try:
            L, A, B = self.readSpins("Lab")
        except InvalidInputError:
            return # don't compute
        r, g, b, l, c, h = rgbLchFromLabInt(L, A, B)
        self.labDisplay.setValues(L, A, B, c, h)
        self.breakColorConnections()
        self.writeRgbText(r, g, b)
        self.writeSpins("RGB", (r, g, b))
        self.writeSpins("LCh", (l, c, h))
        self.updateColor()
        self.makeColorConnections()

    def updateFromLch(self):
        try:
            l, c, h = self.readSpins("LCh")
        except InvalidInputError:
            return # don't compute
        r, g, b, L, A, B = rgbLabFromLchInt(l, c, h)
        self.labDisplay.setValues(L, A, B, c, h)
        self.breakColorConnections()
        self.writeRgbText(r, g, b)
        self.writeSpins("RGB", (r, g, b))
        self.writeSpins("Lab", (L, A, B))
        self.updateColor()
        self.makeColorConnections()

    def updateColor(self):
        self.colorDisplay.setColor(QColor(Qt.transparent) if self.rgbHexInput.text() == "" else QColor.fromRgb(*self.readSpins("RGB")))

app = QApplication([])
mainWindow = MainWindow()
mainWindow.show()
app.exec_()
