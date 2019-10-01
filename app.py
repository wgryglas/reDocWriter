import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKitWidgets import QWebView, QWebPage


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


class MainWindow(QWidget):

    def __init__(self, *args):
        QWidget.__init__(self, *args)

        # QToolBar()
        self.buttons_bar = QWidget()

        self.project_tree = QTreeView()

        self.codeinput = QTextEdit()
        self.codeinput.setFontPointSize(12)

        self.webview = QWebView()
        self.webview.load(QUrl("https://sim-flow.com/"))

        self.layout_toolbar()

        self.layout_components()

    def layout_toolbar(self):
        save = QPushButton("Save")
        undo = QPushButton("Undo")
        redo = QPushButton("Redo")

        repo = QComboBox()
        repo.setEditable(True)
        repo.setMinimumWidth(200)
        repo.addItem("bitbucket@simflow-tutorials")

        commit = QPushButton("Commit")

        layout = QHBoxLayout()
        layout.addWidget(save)
        layout.addSpacing(20)
        layout.addWidget(undo)
        layout.addWidget(redo)
        layout.addStretch(20)
        layout.addWidget(repo)
        layout.addWidget(commit)

        self.buttons_bar.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        # self.buttons_bar.setSizePolicy()
        self.buttons_bar.setLayout(layout)

    def show_url(self, url_string):
        self.webview.load(QUrl(url_string))

    def show_file(self, local_file_path):
        pass

    def layout_components(self):
        container = QSplitter()
        container.setOrientation(Qt.Horizontal)
        container.addWidget(self.project_tree)

        self.project_tree.setMaximumWidth(300)
        container.addWidget(self.codeinput)

        self.codeinput.setMinimumWidth(500)
        container.addWidget(self.webview)

        layout = QVBoxLayout()
        layout.addWidget(self.buttons_bar)
        layout.addWidget(container)

        self.setLayout(layout)



####################################################################
if __name__ == "__main__":
    main()
