
from pyqode.qt.QtWidgets import QWidget


class StatusViewInterface:
    def inform(self, text):
        pass

    def inform_wait(self, text):
        pass

    def release_wait(self):
        pass


class StatusViewTextBar(QWidget, StatusViewInterface):

    def __init__(self):
        QWidget.__init__(self)
        StatusViewInterface.__init__(self)

