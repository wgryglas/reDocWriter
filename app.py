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
from session_panel import SessionPanel
from launcher_panel import InitialPanel
from git_repository import GitRepository
from app_settings import SystemSettings, AppSettings, ColorScheme


class MainWindow(QWidget):
    def __init__(self, app, *args):
        QWidget.__init__(self, *args)
        self.session = None
        self.repo = None
        self.app = app
        self.system = SystemSettings()
        self.settings = AppSettings()

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.launcher = InitialPanel(self.system, self.settings)

        self.main_layout.addWidget(self.launcher)

        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.launcher.on_settings_ready.connect(self.setSettings)
        self.launcher.on_root_selection.connect(self.start_session)

    def closeEvent(self, event):
        self.settings.saveToFile(self.system.settingsFilePath)
        event.accept()

    def setSettings(self, setting):
        self.settings = setting

    def start_session(self, root_path):

        self.launcher.hide()

        if self.session:
            self.session.setParent(None)
            del self.session

        if self.repo:
            del self.repo

        self.repo = GitRepository(root_path)

        self.session = SessionPanel(self.repo, self.app, self.system, self.settings)

        self.set_color_scheme(self.settings.color_scheme)

        # p = self.session.editor.palette()
        # p.setColor(QPalette.Background, QColor(253, 246, 227))
        # self.session.editor.setPalette(p)
        # self.session.editor.setAutoFillBackground(True)
        # self.session.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(self.session)

        if not self.isVisible():
            self.show()

    def set_color_scheme(self, scheme):
        if scheme == ColorScheme.defualt:
            # p = self.palette()
            # p.setColor(QPalette.Background, QColor(253, 246, 227))
            # self.setPalette(p)
            self.setPalette(QPalette())
            # self.setStyleSheet('QPushButton{border:none; margin:4px}')

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
    w = MainWindow(app)
    w.showMaximized()
    # w.start_session(path)
    sys.exit(app.exec_())

####################################################################
if __name__ == "__main__":
    main()

