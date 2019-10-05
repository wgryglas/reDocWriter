import os
import sys
from enum import Enum
os.environ['QT_API'] = 'PySide'
from pyqode.qt.QtCore import *
from pyqode.qt.QtWidgets import *
from pyqode.qt.QtWebWidgets import *
# use custom RstCodeEdit because could not install custom roles to work with linter
from code_edit import RstCodeEdit
from images_panel import ImagesPanel
from sources_panel import SourcesTree
from core import Session
from session_panel import SessionPanel, ColorScheme


class AppSettings:
    def __init__(self):
        self.sort_images = 'date' #name
        self.relative_paths = True
        self.figure_width = '400 px'
        self.editor_font = ''
        self.color_scheme = ColorScheme.defualt
        self.sync_scrolloing = True


class MainWindow(QWidget):
    def __init__(self, app, settings, *args):
        QWidget.__init__(self, *args)
        self.session = None
        self.app = app
        self.settings = settings
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

    def start_session(self, root_path):
        if self.session:
            self.session.setParent(None)

        self.session = SessionPanel(root_path, self.app, self.settings)
        self.main_layout.addWidget(self.session)

        if not self.isVisible():
            self.show()


def main():
    path = '/home/wgryglas/python/pelicanDoc'
    # path = '/home/wgryglas/Code/Python/pelicanReDoc'

    app = QApplication(sys.argv)
    settings = AppSettings()
    w = MainWindow(app, settings)
    w.start_session(path)
    sys.exit(app.exec_())

####################################################################
if __name__ == "__main__":
    main()

