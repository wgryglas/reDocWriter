from pyqode.qt.QtWidgets import QWidget, QSizePolicy, QPushButton


def horizontalSeparator():
    horizontalLineWidget = QWidget()
    horizontalLineWidget.setFixedHeight(1)
    horizontalLineWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    horizontalLineWidget.setStyleSheet("background-color: #c0c0c0;")
    return horizontalLineWidget


class HooverPushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.setStyleSheet('''
            QPushButton {
                 padding:5px;
             }
             QPushButton:hover {
                 border-radius:2px;
                 border: 1px solid #c6c6c6;
                 background: qlineargradient( x1:0 y1:0, x2:0 y2:1, stop:0 #f8f8f8, stop:1 #f1f1f1);
                 color: #5f6368;
             }
             QPushButton:pressed {
                 color: black;
             }
        ''')
        from pyqode.qt.QtWidgets import QGraphicsDropShadowEffect, QColor
        self.effect = QGraphicsDropShadowEffect()
        self.effect.setXOffset(0)
        self.effect.setYOffset(0)
        self.effect.setColor(QColor(200, 200, 200))
        self.effect.setBlurRadius(5)
        self.effect.setEnabled(False)
        self.setGraphicsEffect(self.effect)

    def enterEvent(self, *args, **kwargs):
        QPushButton.enterEvent(self, *args, **kwargs)
        self.effect.setEnabled(True)

    def leaveEvent(self, *args, **kwargs):
        QPushButton.leaveEvent(self, *args, **kwargs)
        self.effect.setEnabled(False)


def hoverActiveButton(*args, **kwargs):
    return HooverPushButton(*args, **kwargs)
