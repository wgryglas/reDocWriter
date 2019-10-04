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
        result = self._command_(*args)
        if result:
            self.when_finished.emit(result)
        else:
            self.when_finished.emit([])  #dummy result so that signal signature will be matched

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


class CopyFiles(UIThread):
    def __init__(self):
        UIThread.__init__(self, 'CopyFiles')

    def _command_(self, *args):
        assert len(args) == 2

        from shutil import copyfile
        import os

        dest_folder = args[0]
        src = args[1]

        print dest_folder
        print src

        for path in src:
            copyfile(path, dest_folder+os.sep+os.path.basename(path))
