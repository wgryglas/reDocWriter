import os
import sys
from enum import Enum
os.environ['QT_API'] = 'PySide'
from pyqode.qt.QtCore import *
from pyqode.qt.QtWidgets import *
# from pyqode.qt.QtWebWidgets import *
# # use custom RstCodeEdit because could not install custom roles to work with linter
# from code_edit import RstCodeEdit
# from images_panel import ImagesPanel
# from sources_panel import SourcesTree
# from core import Session
from session_panel import SessionPanel, ColorScheme
from launcher_panel import LauncherPanel
from git_repository import GitRepository


class MainWindow(QWidget):
    def __init__(self, app, settings, *args):
        QWidget.__init__(self, *args)
        self.session = None
        self.repo = None
        self.app = app
        self.settings = settings
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.launcher = LauncherPanel(settings)
        self.main_layout.addWidget(self.launcher)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.launcher.root_path_selected.connect(self.start_session)

        self.set_color_scheme(self.settings.color_scheme)

    def start_session(self, root_path):

        self.launcher.hide()

        if self.session:
            self.session.setParent(None)
            del self.session

        if self.repo:
            del self.repo

        self.repo = GitRepository(root_path)

        self.session = SessionPanel(self.repo, self.app, self.settings)
        # self.session.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(self.session)

        if not self.isVisible():
            self.show()

    def set_color_scheme(self, scheme):
        if scheme == ColorScheme.defualt:
            self.setPalette(QPalette())
        else:
            self.setStyleSheet("MainWindow{background-color:rgb(37, 37, 37)}")
            # self.setStyleSheet("QPushButton{background-color:rgb(37, 37, 37); border-radius:3px; padding:5px}")
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(37, 37, 37))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)

            self.setPalette(palette)


def main():
    from app_settings import AppSettings

    app = QApplication(sys.argv)
    settings = AppSettings()
    w = MainWindow(app, settings)
    w.showMaximized()
    # w.start_session(path)
    sys.exit(app.exec_())

####################################################################
if __name__ == "__main__":
    main()

