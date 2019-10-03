import os
import sys
import threading

os.environ['QT_API'] = 'PySide'

from enum import Enum
from pyqode.qt.QtCore import *
from pyqode.qt.QtWidgets import *
from pyqode.qt.QtWebWidgets import *
# use custom RstCodeEdit because could not install custom roles to work with linter
from code_edit import RstCodeEdit


class ColorScheme(Enum):
    defualt = 1
    dracula = 2


def main():
    app = QApplication(sys.argv)
    w = MainWindow(app)
    w.show()
    sys.exit(app.exec_())


from core import Session


class MainWindow(QWidget):

    def __init__(self, app, *args):
        QWidget.__init__(self, *args)

        from errors import ErrorHandler, DialogErrorView
        self.errors = ErrorHandler(DialogErrorView(self, app))

        # self.session = Session('/home/wgryglas/python/pelicanDoc', self.errors)
        self.session = Session('/home/wgryglas/Code/Python/pelicanReDoc', self.errors)

        self.buttons_bar = QWidget()

        self.project_tree = QTreeView()

        self.editor = RstCodeEdit(color_scheme='qt', role_names=['lorem'])  # api.CodeEdit()
        # self.codeinput.setFontPointSize(12)

        self.webview = QWebView()

        self.render_timer = None

        # self.webview = HtmlPreviewWidget()
        # self.webview.set_editor(self.editor)

        self.layout_toolbar()

        self.layout_components()

        self.configure_tree()

        self.configure_editor()

        self.render_started = False
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.save_text)

        # address = self.session.start_local_server()
        # fileaddress = '{}my-super-post.html'.format(address)
        # print "serving", fileaddress
        # self.webview.load(QUrl(fileaddress))
        # self.webview.load(QUrl.fromLocalFile('/home/wgryglas/python/pelicanDoc/output/index.html'))
        # self.webview.load( QUrl.fromLocalFile('/home/wgryglas/python/pelicanDoc/output/index.html') )
        self.display_local_html_file(self.session.get_file_output('test.rst'))

        self.text_saved = True

        self.session.html_output_changed.connect(lambda: self.display_local_html_file(self.session.active_file_output))


    def configure_editor(self):
        self.session.content_changed.connect(self.display_new_editor_content)

        self.editor.textChanged.connect(self.mark_unsaved)

        # joining editor with webview
        # self.webview.set_editor(self.editor)

        # self.editor.modes.get()

        # self.editor.backend.start('server.py')

        # append some modes and panels
        # self.editor.modes.append(modes.CodeCompletionMode())
        # self.editor.modes.append(modes.PygmentsSyntaxHighlighter(self.editor.document()))
        # self.editor.modes.append(modes.CaretLineHighlighterMode())
        # self.editor.panels.append(panels.SearchAndReplacePanel(), api.Panel.Position.BOTTOM)

        # self.editor.modes.get(PygmentsSyntaxHighlighter).pygments_style = 'monokai'

    def mark_unsaved(self):
        self.text_saved = False
        if not self.render_started:
            self.render_timer.start(1000)
            self.render_started = True

    def save_text(self):
        if not self.text_saved:
            self.text_saved = True
            self.session.set_active_file_content(self.editor.toPlainText())


    def configure_tree(self):
        from uimodels import create_directory_tree_model
        model = create_directory_tree_model(self.session.get_sources_structure())
        self.project_tree.setModel(model)

        selection_model = QItemSelectionModel(model)
        selection_model.selectionChanged.connect(self._on_file_selection_)

        self.project_tree.setSelectionModel(selection_model)
        self.project_tree.setSelectionMode(QAbstractItemView.SingleSelection)

    def _on_file_selection_(self, qindex, flags):
        index = self.project_tree.selectedIndexes()[0]
        item = index.model().itemFromIndex(index)
        node = item.data()

        if not node.is_dir:
            self.session.set_active_file(node.local_path)

    def display_new_editor_content(self, content):
        self.editor.clear()
        self.editor.setPlainText(content)
        self.text_saved = True

    def display_local_html_file(self, file_path_string):
        import os
        if not file_path_string:
            self.errors.show("Can't show Null html file")
            return

        if not os.path.exists(file_path_string):
            self.errors.show('Could not load html file {} because it does not exist'.format(file_path_string))
        else:
            self.webview.load(QUrl.fromLocalFile(file_path_string))

    def display_url(self, url_string):
        self.webview.load(QUrl(url_string))

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

    def set_color_scheme(self, scheme):
        if scheme == ColorScheme.defualt:
            self.setPalette(QPalette())
        else:
            # self.setStyleSheet("MainWindow{background-color:rgb(37, 37, 37)}")
            self.setStyleSheet("QPushButton{background-color:rgb(37, 37, 37)}")
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


####################################################################
if __name__ == "__main__":
    main()

