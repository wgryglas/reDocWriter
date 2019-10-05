from pyqode.qt.QtCore import Signal, QSize, Qt
from pyqode.qt.QtGui import QIcon
from pyqode.qt.QtWidgets import QWidget, QTreeView, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSizePolicy, QStyle, QItemSelectionModel, QAbstractItemView
from pyqode.qt.QtGui import QStandardItemModel, QStandardItem


def alwaysTrue(*args):
    return True


def create_directory_tree_model(component, root_tree, file_filter=alwaysTrue, folder_filter=alwaysTrue):
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels([root_tree.name])

    mapping = {root_tree: model}

    for parent, files, dirs in root_tree.walk():
        if parent not in mapping:
            continue

        parent_item = mapping[parent]
        for f in filter(file_filter, files):
            fitem = QStandardItem(f.name)
            fitem.setIcon(component.style().standardIcon(QStyle.SP_FileIcon))
            fitem.setData(f)
            parent_item.appendRow(fitem)

        for d in filter(folder_filter, dirs):
            ditem = QStandardItem(d.name)
            ditem.setIcon(component.style().standardIcon(QStyle.SP_DirIcon))
            ditem.setData(d)
            mapping[d] = ditem
            parent_item.appendRow(ditem)

    return model


class SourcesTree(QWidget):

    source_selection_changed = Signal(object)

    def __init__(self, session, errors):
        QWidget.__init__(self)
        self._session_ = session
        self._errors_ = errors

        session.sources_changed.connect(self.update_model)

        self.tree = QTreeView()
        self.buttons_bar = QWidget()
        self.add_folder = QPushButton()
        self.add_folder.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        self.add_folder.setToolTip('Add folder')

        self.add_page = QPushButton()
        self.add_page.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        self.add_page.setToolTip('Add new page')

        self.delete_button = QPushButton()
        self.delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.delete_button.setToolTip('Delete selected page/folder')

        self._update_buttons_state_()
        self.source_selection_changed.connect(self._update_buttons_state_)

        self._do_layout_()

    def _do_layout_(self):
        self._layout_buttons_()
        box = QVBoxLayout()
        box.addWidget(self.buttons_bar)
        box.addWidget(self.tree)
        self.setLayout(box)

    def _layout_buttons_(self):
        box = QHBoxLayout()
        box.addWidget(self.delete_button)
        box.addStretch(20)
        box.addWidget(self.add_folder)
        box.addWidget(self.add_page)
        box.setContentsMargins(0, 5, 5, 0)
        self.buttons_bar.setLayout(box)
        self.buttons_bar.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))

    def _update_buttons_state_(self):
        flag = self.is_any_selected()
        self.add_page.setEnabled(flag)
        self.add_folder.setEnabled(flag)
        self.delete_button.setEnabled(flag)

    def update_model(self):

        model = create_directory_tree_model(self.tree,
                                            self._session_.get_sources_structure(),
                                            file_filter=lambda f: f.name.endswith('.rst'),
                                            folder_filter=lambda d: d.name != 'figures')
        self.tree.setModel(model)

        selection_model = QItemSelectionModel(model)
        selection_model.selectionChanged.connect(lambda: self.source_selection_changed.emit(self.get_selected_file()))

        self.tree.setSelectionModel(selection_model)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)

    def is_any_selected(self):
        return len(self.tree.selectedIndexes()) > 0

    def get_selected_file(self):
        selection = self.tree.selectedIndexes()
        if len(selection) == 0:
            return None
        index = selection[0]
        item = index.model().itemFromIndex(index)
        return item.data()