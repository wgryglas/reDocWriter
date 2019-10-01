import os
import sys

os.environ['QT_API'] = 'PyQt4'

from pyqode.qt.QtCore import *
from pyqode.qt.QtWidgets import *
from pyqode.qt.QtWebWidgets import *
from pyqode.rst.widgets import RstCodeEdit


def main():
    app = QApplication(sys.argv)
    w = MainWindow(app)
    w.show()
    sys.exit(app.exec_())


class MainWindow(QWidget):

    def __init__(self, app, *args):
        QWidget.__init__(self, *args)

        from errors import ErrorHandler, DialogErrorView
        self.errors = ErrorHandler(DialogErrorView(self, app))

        # QToolBar()
        self.buttons_bar = QWidget()

        self.project_tree = QTreeView()

        self.editor = RstCodeEdit(color_scheme='qt')#api.CodeEdit()
        # self.codeinput.setFontPointSize(12)

        self.webview = QWebView()
        self.webview.load(QUrl("https://sim-flow.com/"))

        # self.webview = HtmlPreviewWidget()
        # self.webview.set_editor(self.editor)

        self.layout_toolbar()

        self.layout_components()

        self.configure_editor()

    def configure_editor(self):
        pass
        # joining editor with webview
        #self.webview.set_editor(self.editor)

        # self.editor.modes.get()

        # self.editor.backend.start('server.py')

        # append some modes and panels
        # self.editor.modes.append(modes.CodeCompletionMode())
        # self.editor.modes.append(modes.PygmentsSyntaxHighlighter(self.editor.document()))
        # self.editor.modes.append(modes.CaretLineHighlighterMode())
        # self.editor.panels.append(panels.SearchAndReplacePanel(), api.Panel.Position.BOTTOM)

        # self.editor.modes.get(PygmentsSyntaxHighlighter).pygments_style = 'monokai'

    def layout_toolbar(self):
        save = QPushButton("Save")
        save.clicked.connect(lambda: self.errors.show("Hi, nice to meet you"))

        undo = QPushButton("Undo")
        undo.clicked.connect(lambda: self.editor.undo())

        redo = QPushButton("Redo")
        redo.clicked.connect(lambda: self.editor.redo())

        repo = QComboBox()
        repo.setEditable(True)
        repo.setMinimumWidth(200)
        repo.addItem("bitbucket@simflow-tutorials")

        update = QPushButton("Update")
        update.clicked.connect(lambda: self.errors.ask_yes_no("Do you?"))


        commit = QPushButton("Commit")

        layout = QHBoxLayout()
        layout.addWidget(save)
        layout.addSpacing(20)
        layout.addWidget(undo)
        layout.addWidget(redo)
        layout.addStretch(20)
        layout.addWidget(repo)
        layout.addSpacing(20)
        layout.addWidget(update)
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
        container.addWidget(self.editor)

        self.editor.setMinimumWidth(500)
        container.addWidget(self.webview)

        layout = QVBoxLayout()
        layout.addWidget(self.buttons_bar)
        layout.addWidget(container)

        self.setLayout(layout)



####################################################################
if __name__ == "__main__":
    main()
