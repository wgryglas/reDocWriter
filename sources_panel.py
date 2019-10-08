from pyqode.qt.QtCore import Signal, QSize, Qt
from pyqode.qt.QtGui import QIcon
from pyqode.qt.QtWidgets import QWidget, QFrame, QTreeView, QVBoxLayout, QPushButton, QHBoxLayout, \
    QSizePolicy, QStyle, QItemSelectionModel, QAbstractItemView, QDialog, QToolButton, QGraphicsDropShadowEffect, \
    QLineEdit, QLabel, QValidator
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


def _create_shadow_():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(10)
    shadow.setXOffset(0)
    shadow.setYOffset(3)
    return shadow


class FileExistValidator(QValidator):
    def __init__(self, session):
        QValidator.__init__(self)
        self.session = session

    def validate(self, text, text_pos):
        from os import walk
        from os.path import dirname
        dir_path = dirname(self.session.active_full_path)
        p, dirs, files = walk(dir_path).next()
        fname = text.strip() + '.rst'
        value = QValidator.Acceptable
        if fname in files:
            value = QValidator.Intermediate

        return value, text, text_pos


class AddNewTemplatePanel(QDialog):
    template_selected = Signal(str)
    on_file_create = Signal(str, str)

    def __init__(self, parent, session):
        QDialog.__init__(self, parent)
        self.setStyleSheet('''
        QToolButton { 
            border: 1px solid rgb(51, 122, 183); 
            border-radius:5px; 
            background:rgb(222, 222, 222); 
            outline:0px;
            padding:10px;
            width: 80px;
        } 
        QToolButton:hover { background:transparent; background:rgb(51, 122, 183); color:white}
        QToolButton:pressed { background:rgb(41, 100, 153); color:white }
        QToolButton:checked { background:rgb(41, 100, 153); color:white }
        ''')

        self.setWindowTitle('Choose Template')

        self.boxLt = QHBoxLayout()
        self.boxLt.setSpacing(20)
        self.buttons = {}
        self.selected = None

        nameLt = QHBoxLayout()
        self.nameInput = QLineEdit()
        self.nameInput.setValidator(FileExistValidator(session))
        nameLt.addWidget(QLabel('File Name'))
        nameLt.addSpacing(10)
        nameLt.addWidget(self.nameInput)
        self.errorLabel = QLabel('File already exists, change name')
        self.errorLabel.setStyleSheet('color:red; font-size:8pt')
        self.errorLabel.hide()

        self.create = QPushButton('Create')
        self.create.setEnabled(False)
        self.create.clicked.connect(self.processCreation)
        blt = QHBoxLayout()
        blt.addStretch(0)
        blt.addWidget(self.create)

        lt = QVBoxLayout()
        lt.addLayout(nameLt)
        lt.addWidget(self.errorLabel)
        lt.addSpacing(20)
        lt.addLayout(self.boxLt)
        lt.addSpacing(20)
        lt.addLayout(blt)
        lt.setContentsMargins(50, 50, 50, 50)
        self.setLayout(lt)

        self.template_selected.connect(self.validateCreate)
        self.nameInput.textChanged.connect(self.validateCreate)

    def populateButtons(self, names):
        self.buttons = {}
        for name in names:
            b = QToolButton()
            b.setText(name)
            b.setGraphicsEffect(_create_shadow_())
            b.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            b.clicked.connect(self.processTemplateClick)
            b.setCheckable(True)
            self.buttons[name] = b
            self.boxLt.addWidget(b)

    def validateCreate(self):
        correct_name = self.nameInput.hasAcceptableInput()
        enabled = sum([int(self.buttons[b].isChecked()) for b in self.buttons]) == 1 and len(self.nameInput.text()) > 0 and correct_name
        self.create.setEnabled(enabled)
        self.errorLabel.setVisible(not correct_name)

    def processTemplateClick(self):
        bname = self.sender().text()
        for name in self.buttons:
            if name != bname:
                self.buttons[name].setChecked(False)
        self.selected = bname
        self.template_selected.emit(self.sender().text())

    def processCreation(self):
        self.on_file_create.emit(self.nameInput.text().strip(), self.selected)


class SourcesTree(QWidget):

    source_selection_changed = Signal(object)

    def __init__(self, session, system, errors):
        QWidget.__init__(self)
        self._session_ = session
        self._errors_ = errors
        self.system = system

        session.sources_changed.connect(self.update_model)

        self.tree = QTreeView()
        self.buttons_bar = QFrame()
        self.add_folder = QPushButton()
        self.add_folder.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        self.add_folder.setToolTip('Add folder')

        self.add_page = QPushButton()
        self.add_page.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        self.add_page.setToolTip('Add new page')
        self.add_page.clicked.connect(self.showNewPageWindow)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.delete_button.setToolTip('Delete selected page/folder')

        self._update_buttons_state_()
        self.source_selection_changed.connect(self._update_buttons_state_)

        self._do_layout_()

    def _do_layout_(self):
        self._layout_buttons_()
        box = QVBoxLayout()
        box.setSpacing(0)
        box.addWidget(self.buttons_bar)
        box.addWidget(self.tree)

        self.setLayout(box)

    def _layout_buttons_(self):
        box = QHBoxLayout()
        box.addWidget(self.delete_button)
        box.addStretch(20)
        box.addWidget(self.add_folder)
        box.addWidget(self.add_page)
        box.setContentsMargins(5, 5, 5, 5)
        self.buttons_bar.setLayout(box)
        self.buttons_bar.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.buttons_bar.setObjectName('buttons')
        self.buttons_bar.setStyleSheet('QFrame#buttons{background:transparent; border-top:1px solid gray; '
                                       'border-left:1px solid gray; border-right:1px solid gray; '
                                       'border-top-left-radius:3px; border-top-right-radius:3px}')

    def _update_buttons_state_(self):
        flag = self.is_any_selected()
        self.add_page.setEnabled(flag)
        self.add_folder.setEnabled(flag)
        self.delete_button.setEnabled(flag)

    def update_model(self):
        toSelect = self.get_selected_file()

        model = create_directory_tree_model(self.tree,
                                            self._session_.get_sources_structure(),
                                            file_filter=lambda f: f.name.endswith('.rst'),
                                            folder_filter=lambda d: d.name != 'figures')
        self.tree.setModel(model)

        selection_model = QItemSelectionModel(model)
        selection_model.selectionChanged.connect(lambda: self.source_selection_changed.emit(self.get_selected_file()))

        self.tree.setSelectionModel(selection_model)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)

        if toSelect:
            self.setSelectedFile(toSelect)

    def is_any_selected(self):
        return len(self.tree.selectedIndexes()) > 0

    def get_selected_file(self):
        selection = self.tree.selectedIndexes()
        if len(selection) == 0:
            return None
        index = selection[0]
        item = index.model().itemFromIndex(index)
        return item.data()

    def showNewPageWindow(self):
        from os.path import basename
        dialog = AddNewTemplatePanel(self, self._session_)
        names = ['Empty']
        for name in [basename(path).split('.')[0] for path in self.system.templateFiles]:
            names.append(name)
        dialog.populateButtons(names)
        dialog.on_file_create.connect(self.addNewFile)
        dialog.on_file_create.connect(lambda f, t: dialog.close())
        dialog.open()

    def addNewFile(self, fileName, templateName):
        from os.path import basename, dirname
        from os import sep

        dest = '{}{}{}.rst'.format(dirname(self._session_.active_full_path), sep, fileName)

        if templateName == 'Empty':
            self._session_.addEmptyToSrc(dest)
        else:
            sourcePath = None
            for path in self.system.templateFiles:
                if templateName == basename(path).split('.')[0]:
                    sourcePath = path
                    break
            if sourcePath is None:
                self._errors_.show("Couldn't find path to template file")
                return
            self._session_.addCopyToSrc(sourcePath, dest)

    def setSelectedFile(self, fileObj):
        items = self.tree.model().findItems(fileObj.name)
        for item in items:
            if item.data().full_path == fileObj.full_path:
                self.tree.selectionModel().setCurrentIndex(item.index(), QItemSelectionModel.Select)
                return


if __name__ == '__main__':
    import sys
    from pyqode.qt.QtWidgets import QApplication

    def displ(s):
        print s

    class SessionMokup:
        def __init__(self):
            self.active_full_path = '/home/wgryglas/python/pelicanDoc/content/test.rst'

    app = QApplication(sys.argv)

    p = AddNewTemplatePanel(SessionMokup())
    p.populateButtons(['Empty', 'Tutorial', 'Article'])
    p.show()
    p.template_selected.connect(displ)

    sys.exit(app.exec_())