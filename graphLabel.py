# GraphLabel widget
# =================
#
# Copyright (C) 2019, Shriramana Sharma, samjnaa-at-gmail-dot-com
#
# Use, modification and distribution are permitted subject to the
# "BSD-2-Clause"-type license stated in the accompanying file LICENSE.txt

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class GraphLabel(QLabel):

    focusChanged = pyqtSignal(int, int)

    def __init__(self, graphParent, xSize, ySize):
        QLabel.__init__(self)
        self.graphParent = graphParent
        self.setFixedSize(xSize, ySize)
        self.setFrameShape(QFrame.Box)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.focusChanged.emit(event.pos().x(), event.pos().y())
        elif event.button() == Qt.RightButton:
            fname = QFileDialog.getSaveFileName(self, "RGB2LAB GUI: Save “{}” graph".format(self.graphParent.graphName), QDir.homePath(), "PNG images (*.png)")[0]
            if fname == "":
                return
            if not self.graphParent.image.save(fname, "PNG"):
                QMessageBox.critical(self, "RGB2LAB GUI: Error", "Could not save the image to the chosen path. Perhaps the path is not writable. Please try again.")

