
from pyqode.qt.QtCore import Signal, QSize, Qt
from pyqode.qt.QtGui import QIcon
from pyqode.qt.QtWidgets import QWidget, QTreeView, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSizePolicy, QStyle, QItemSelectionModel, QAbstractItemView
from pyqode.qt.QtGui import QStandardItemModel, QStandardItem



class EditorPanel(QWidget):
    code_changed = Signal()

    def __init__(self):
        QWidget.__init__(self)





    def _do_buttons_layout_(self):
        pass

    def _do_layout_(self):
        pass