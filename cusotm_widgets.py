from pyqode.qt.QtWidgets import QPushButton, QFrame
from pyqode.qt.QtCore import  QRect


class LinkLikeButton(QPushButton):
    def __init__(self, text):
        QPushButton.__init__(self, text)
        self.setStyleSheet('background-color:transparent; color:rgb(51, 122, 183); text-align:left; outline:0px')

    def _underline_(self, flag):
        font = self.font()
        font.setUnderline(flag)
        self.setFont(font)

    def enterEvent(self, event):
        self._underline_(True)

    def leaveEvent(self, event):
        self._underline_(False)


class SepartorLine(QFrame):
    def __init__(self, width):
        QFrame.__init__(self)
        # self.setObjectName(QString.fromUtf8("line"))
        self.setGeometry(QRect(320, 150, 118, 3))
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)