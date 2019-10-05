from pyqode.qt.QtWidgets import QPushButton, QFrame
from pyqode.qt.QtGui import QPalette, QColor


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
    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class ThinLine(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.HLine)
        self.setContentsMargins(0, 0, 0, 0)
        pal = self.palette()
        pal.setColor(QPalette.Foreground, QColor(150, 150, 150))
        self.setPalette(pal)

