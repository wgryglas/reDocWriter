from pyqode.qt.QtCore import Signal, QSize, Qt
from pyqode.qt.QtGui import QIcon
from pyqode.qt.QtWidgets import QWidget, QTreeView, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSizePolicy, QStyle

class SourcesTree(QWidget):

    def __init__(self):
        self.tree = QTreeView()

