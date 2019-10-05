from pyqode.qt.QtCore import Signal, QSize, Qt
from pyqode.qt.QtGui import QIcon
from pyqode.qt.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSizePolicy, QStyle, QFileDialog
from uitreads import LoadPixmaps, DeleteFiles


class ImagesPanel(QWidget):
    on_insert_image = Signal(object)

    def __init__(self, session, settings):
        QWidget.__init__(self)

        self._settings_ = settings
        self._session_ = session
        self.visible_files = []
        self.selected_file = None

        self.list = QListWidget()
        self.list.itemSelectionChanged.connect(self._handle_selection_)

        self.buttons_bar = QWidget()

        self.insert_button = QPushButton()
        self.insert_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.insert_button.setToolTip('Insert as image')
        self.insert_button.clicked.connect(self._do_insert_)

        self.add_files_button = QPushButton()
        self.add_files_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.add_files_button.setToolTip('Import images to repository')
        self.add_files_button.clicked.connect(self._open_import_)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.delete_button.setToolTip('Delete selected images')
        self.delete_button.clicked.connect(self._delete_selection_)

        self._revalidate_()

        self._do_layout_()

    def _layout_buttons_(self):
        box = QHBoxLayout()
        box.setContentsMargins(0, 5, 5, 0)
        box.addWidget(self.add_files_button)
        box.addWidget(self.delete_button)
        box.addStretch(20)
        box.addWidget(self.insert_button)
        self.buttons_bar.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.buttons_bar.setLayout(box)

    def _do_layout_(self):
        box = QVBoxLayout()
        box.setContentsMargins(0, 0, 0, 0)
        box.addWidget(self.buttons_bar)
        box.addWidget(self.list)
        self._layout_buttons_()
        self.setLayout(box)

    def _configure_list_(self):
        self.list.setSelectionMode(QListWidget.SingleSelection)
        # self.list.setFlow(QListWidget.LeftToRight)
        self.list.setViewMode(QListWidget.ListMode)
        # self.list.setWrapping(True)
        # self.list.setWordWrap(True)
        self.list.setIconSize(QSize(60, 60))
        # self.list.setMovement(QListWidget.Static)
        # self.list.setMaximumHeight(400)
        # self.list.setResizeMode(QListWidget.Adjust)

    def _revalidate_(self):
        enabled = self.selected_file is not None
        self.delete_button.setEnabled(enabled)
        self.insert_button.setEnabled(enabled)
        if self._session_.is_file_set:
            self.show_source_images(self._session_.active_local_path)

    def _display_pixmaps_(self, files, pixmaps):
        from utils import argsort, reordered, creation_date

        if self._settings_.sort_images == 'name':
            sorting = argsort(files, key=lambda f: f.name.lower())
        else:
            sorting = argsort(files, key=lambda f: creation_date(f.full_path))

        self.visible_files = reordered(files, sorting)

        for f, img in zip(self.visible_files, reordered(pixmaps, sorting)):
            icon = QIcon()
            icon.addPixmap(img)
            item = QListWidgetItem(icon, f.name.split('.')[0])
            item.setTextAlignment(Qt.AlignBottom)
            item.setToolTip(f.local_path)
            item.setData(QListWidgetItem.UserType, f)
            # item.setSizeHint(QSize(120, 80))
            self.list.addItem(item)

    def show_source_images(self, source_local_path):
        image_files = self._session_.get_figures_files_for(source_local_path)
        self.display_figures(image_files)

    @property
    def isAnySelected(self):
        return self.selected_file is not None

    def display_figures(self, files):
        self.list.clear()
        self._configure_list_()
        self.selected_file = None

        paths = map(lambda f: f.full_path, files)

        thread = LoadPixmaps()
        thread.when_finished.connect(lambda maps: self._display_pixmaps_(files, paths))
        thread.start(paths)

    def _handle_selection_(self):
        enabled = len(self.list.selectedItems()) > 0

        self.insert_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

        if enabled:
            index = self.list.selectedIndexes()[0].row()
            self.selected_file = self.visible_files[index]

    def _do_insert_(self):
        path = self.selected_file.local_path if self._settings_.relative_paths else self.selected_file.full_path
        self.on_insert_image.emit(path)

    def _open_import_(self):
        from uitreads import CopyFiles

        folder = self._session_.active_file_figures_folder
        dialog = QFileDialog()
        # dialog.setFileMode(QFileDialog.ExistingFiles)
        # dialog.setModal(True)
        names = dialog.getOpenFileNames(self, 'Import images', folder.full_path, 'PNG (*.png);;JPG (*.jpg)')[0]

        copy_op = CopyFiles()
        copy_op.when_finished.connect(lambda _: self.show_source_images(self._session_.active_local_path))
        copy_op.start(folder.full_path, names)

    def _delete_selection_(self):
        if self.isAnySelected:
            delete_op = DeleteFiles()
            delete_op.when_finished.connect(self._revalidate_)
            delete_op.start([self.selected_file.full_path])
