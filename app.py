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
from images_panel import ImagesPanel

class ColorScheme(Enum):
    defualt = 1
    dracula = 2


def main():
    app = QApplication(sys.argv)
    w = MainWindow(app)
    w.show()
    sys.exit(app.exec_())

from core import Session


class Settings:
    def __init__(self):
        self.sort_images = 'date' #name
        self.relative_paths = False
        self.figure_scale = '50 %'
        self.editor_font = 'Mono'


class MainWindow(QWidget):

    def __init__(self, app, *args):
        QWidget.__init__(self, *args)

        from errors import ErrorHandler, DialogErrorView

        self.settings = Settings()

        self.errors = ErrorHandler(DialogErrorView(self, app))

        # self.session = Session('/home/wgryglas/python/pelicanDoc', self.errors)
        self.session = Session('/home/wgryglas/Code/Python/pelicanReDoc', self.errors)

        self.buttons_bar = QWidget()

        self.project_tree = QTreeView()

        self.editor = RstCodeEdit(color_scheme='qt')  # api.CodeEdit()
        self.editor.font_name = self.settings.editor_font

        # self.codeinput.setFontPointSize(12)

        self.webview = QWebView()

        self.images_gallery = ImagesPanel(self.session, self.settings)

        # self.webview = HtmlPreviewWidget()
        # self.webview.set_editor(self.editor)

        self.layout_toolbar()

        self.layout_components()

        self.configure_tree()

        self.configure_editor()

        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.save_text)

        self.text_saved = True

        # address = self.session.start_local_server()
        # fileaddress = '{}my-super-post.html'.format(address)
        # print "serving", fileaddress
        # self.webview.load(QUrl(fileaddress))
        # self.webview.load(QUrl.fromLocalFile('/home/wgryglas/python/pelicanDoc/output/index.html'))
        # self.webview.load( QUrl.fromLocalFile('/home/wgryglas/python/pelicanDoc/output/index.html') )
        self.display_local_html_file(self.session.get_file_output('test.rst'))

        self.session.html_output_changed.connect(lambda: self.display_local_html_file(self.session.active_file_output))

        self.session.html_content_changed.connect(lambda: self.webview.reload())

        self.images_gallery.on_insert_image.connect(self.insert_image_in_current_position)


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

    def insert_directive_in_current_position(self, text):
        # assert dictionary is placed in new line
        if self.editor.textCursor().columnNumber() > 0:
            text = '\n'+text
        self.editor.insertPlainText(text)

    def insert_image_in_current_position(self, path):
        from editr_actions import format_image
        self.insert_directive_in_current_position(format_image(path, scale=self.settings.figure_scale))

    def mark_unsaved(self):
        self.text_saved = False
        if not self.render_timer.isActive():
            self.render_timer.start(1000)

    def save_text(self):
        if not self.text_saved:
            self.text_saved = True
            self.session.set_active_file_content(self.editor.toPlainText())

    def configure_tree(self):
        from uimodels import create_directory_tree_model
        model = create_directory_tree_model(self.session.get_sources_structure(),
                                            file_filter=lambda f: f.name.endswith('.rst'),
                                            folder_filter=lambda d: d.name != 'figures')
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
            self.images_gallery.show_source_images(node.local_path)

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

        left_widget = QSplitter()
        left_widget.setMaximumWidth(300)
        left_widget.setOrientation(Qt.Vertical)
        left_widget.addWidget(self.project_tree)
        left_widget.addWidget(self.images_gallery)

        container.addWidget(left_widget)

        container.addWidget(self.editor)
        self.editor.setMinimumWidth(600)

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

