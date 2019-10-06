from pyqode.qt.QtCore import *
from pyqode.qt.QtWidgets import *
from pyqode.qt.QtWebWidgets import *
from images_panel import ImagesPanel
from sources_panel import SourcesTree
from core import Session
from app_settings import ColorScheme
from git_repository import GitRepository
from uitreads import CustomRoutine
from files import find_first_file
from cusotm_widgets import ThinLine
from editor_panel import EditorPanel


class SessionPanel(QWidget):

    def __init__(self, gitRepo, app, settings):
        QWidget.__init__(self)

        from errors import ErrorHandler, DialogErrorView

        self.settings = settings

        self.errors = ErrorHandler(DialogErrorView(self, app))

        self.session = Session(gitRepo, self.errors)

        self.text_saved = True

        self.buttons_bar = QWidget()

        self.project_tree = SourcesTree(self.session, self.errors)
        self.project_tree.source_selection_changed.connect(self._on_file_selection_)
        self.session.sources_changed.connect(self.project_tree.update_model)

        self.editor = EditorPanel(self.settings)
        self.session.content_changed.connect(self.editor.displayText)
        self.editor.content_changed.connect(lambda: self.session.set_active_file_content(self.editor.plainText))

        self.webview = QWebView()

        self.images_gallery = ImagesPanel(self.session, self.settings)

        self.session.html_output_changed.connect(lambda: self.display_local_html_file(self.session.active_file_output))

        self.session.html_content_changed.connect(lambda: self.webview.reload())

        self.images_gallery.on_insert_image.connect(self.insert_image_in_current_position)

        self.layout_toolbar()

        self.layout_components()

        self.session.start()

        any_file = find_first_file(self.session.get_sources_structure())
        if any_file:
            self.project_tree.setSelectedFile(any_file)

    def setSyncScrolling(self, flag):
        if flag:
            self.editor.verticalScrollBar().valueChanged.connect(self._sync_webview_scroll_)
        else:
            self.editor.verticalScrollBar().valueChanged.disconnect(self._sync_webview_scroll_)

    def _sync_webview_scroll_(self, value):
        scrollRange = self.editor.verticalScrollBar().maximum()
        if scrollRange == 0:
            return
        fraction = float(value) / scrollRange
        frame = self.webview.page().mainFrame()
        pnt = frame.scrollPosition()
        size = frame.contentsSize()
        self.webview.page().mainFrame().setScrollPosition(QPoint(pnt.x(), fraction * size.height()))

    def insert_image_in_current_position(self, path):
        from editr_actions import format_image
        self.editor.insert_directive_in_current_position(format_image(path, width=self.settings.figure_width))

    def _on_file_selection_(self, selected_file):
        if selected_file and not selected_file.is_dir:
            self.session.set_active_file(selected_file.local_path)
            self.images_gallery.show_source_images(selected_file.local_path)

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
        # save = QPushButton("Save")
        # save.clicked.connect(lambda: self.errors.show("Hi, nice to meet you"))

        # sync_scroll = QSlideSwitch()
        sync_scroll = QCheckBox()
        sync_scroll.setText('Sync Scroll')
        sync_scroll.clicked.connect(lambda: self.setSyncScrolling(sync_scroll.isChecked()))
        if self.settings.sync_scrolling:
            sync_scroll.animateClick()

        repo = QComboBox()
        repo.setEditable(True)
        repo.setMinimumWidth(200)

        remote = self.session.remote_address

        # Async repos check
        repo.addItem(remote.split(':')[1])

        def collect_repo_names(local_dirs):
            collection = []
            print local_dirs
            for recent in local_dirs:
                r = GitRepository(recent)
                if r.address != remote:
                    collection.append(r.address.split(':')[1])
            return collection

        def apply_names(names):
            print names
            for name in names:
                repo.addItem(name)

        collect_repos = CustomRoutine(collect_repo_names)
        collect_repos.when_finished.connect(apply_names)
        collect_repos.start(self.settings.recent_existing)

        # UI thread repos check
        # repo.addItem(remote.split(':')[1])
        # for recent in self.settings.recent_existing:
        #     r = GitRepository(recent)
        #     if r.address != remote:
        #         repo.addItem(r.address.split(':')[1])

        update = QPushButton("Update")
        update.clicked.connect(lambda: self.errors.ask_yes_no("Do you?"))

        commit = QPushButton("Commit")

        layout = QHBoxLayout()
        layout.addStretch(0)
        layout.addWidget(sync_scroll)
        layout.addStretch(0)
        layout.addWidget(repo)
        layout.addSpacing(20)
        layout.addWidget(update)
        layout.addWidget(commit)

        self.buttons_bar.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.buttons_bar.setLayout(layout)

    def show_url(self, url_string):
        self.webview.load(QUrl(url_string))

    def layout_components(self):
        container = QSplitter()
        container.setOrientation(Qt.Horizontal)

        left_widget = QSplitter()
        pal = left_widget.palette()
        pal.setColor(QPalette.Background, QColor(226, 226, 226))
        left_widget.setPalette(pal)
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
        layout.setSpacing(0)
        layout.addWidget(ThinLine())
        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)


