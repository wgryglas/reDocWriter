import threading
from pyqode.qt.QtCore import QObject, Signal
from pyqode.qt.QtGui import QPixmap


class UIThread(QObject):
    when_finished = Signal(object)

    def __init__(self, name):
        QObject.__init__(self)
        # self.callback = callback
        self.name = name
        # self.when_finished.connect(callback)

    def _command_(self, *args):
        pass

    def _exec_function_(self, *args):
        self.when_finished.emit(self._command_(*args))

    def start(self, *args):
        t = threading.Thread(name=self.name, target=self._exec_function_, args=args)
        t.start()


class LoadPixmaps(UIThread):

    def __init__(self):
        UIThread.__init__(self, 'LoadPixmaps')

    def _command_(self, *args):
        assert len(args) == 1
        paths = args[0]
        return map(QPixmap, paths)


