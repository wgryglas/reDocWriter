
from pyqode.qt.QtCore import Signal, Qt
from pyqode.qt.QtWidgets import QDialog, QPushButton, QStyle, QVBoxLayout, QHBoxLayout


class OKCancelDialog(QDialog):
    on_ok = Signal()
    on_close = Signal()

    def __init__(self, centeralWidget):
        QDialog.__init__(self)

        ok = QPushButton()
        ok.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        ok.setText('Ok')
        ok.clicked.connect(self.on_ok.emit)
        ok.clicked.connect(lambda: self.close())

        cancel = QPushButton()
        cancel.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        cancel.setText('Cancel')
        cancel.clicked.connect(lambda: self.close())

        buttonsLt = QHBoxLayout()
        buttonsLt.addStretch()
        buttonsLt.addWidget(ok)
        buttonsLt.addWidget(cancel)

        mainLt = QVBoxLayout()
        mainLt.addWidget(centeralWidget, Qt.AlignCenter)
        mainLt.addLayout(buttonsLt)

        self.setLayout(mainLt)

    def closeEvent(self, QCloseEvent):
        self.on_close.emit()
