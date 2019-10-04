from pyqode.qt.QtCore import Signal, QSize, Qt
from pyqode.qt.QtGui import QIcon
from pyqode.qt.QtWidgets import QWidget, QTreeView, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSizePolicy, QStyle

class SourcesTree(QWidget):

    def __init__(self, session, errors):
        self.tree = QTreeView()
        self._session_ = session
        self._errors_ = errors

    def show_sources_for(self, local_file_path):
        pass
