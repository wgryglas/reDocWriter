from pyqode.qt.QtCore import *
from pyqode.qt.QtWidgets import *
from cusotm_widgets import LinkLikeButton, SepartorLine
from app_settings import SystemSettings
from git_repository import GitRepository


def _title_label_(text):
    label = QLabel()
    label.setText(text)
    label.setStyleSheet('font-size:18pt')
    return label


def _make_form_row_(label, inline_cmpt, *args):
    parent = QWidget()
    lt = QHBoxLayout()
    lt.setContentsMargins(0, 0, 0, 0)
    label = QLabel(label)
    label.setMinimumWidth(100)
    lt.addWidget(label)
    lt.addWidget(inline_cmpt)

    tot_w = 0
    for cmpt in args:
        tot_w += cmpt.size().width()

    inline_cmpt.setMaximumWidth(400-tot_w-10)
    lt.setSpacing(0)
    for cmpt in args:
        lt.addWidget(cmpt)

    parent.setLayout(lt)

    return parent


class LauncherPanel(QWidget):
    root_path_selected = Signal(str)

    def __init__(self, settings):
        QWidget.__init__(self)

        self.settings = settings

        self.git_address = QLineEdit()
        self.local_path = QLineEdit()
        self.open_loc_button = QPushButton()
        self.open_loc_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.open_loc_button.setToolTip('Select location from your hard drive')
        self.clone_button = QPushButton('Clone')

        self._do_layout_()

    def _do_layout_(self):
        lt = QVBoxLayout()
        lt.addStretch(50)
        lt.addWidget(_title_label_('Recent'))
        for recent in self.settings.recent_existing:
            git = GitRepository(recent)
            button = LinkLikeButton('{} ({})'.format(recent, git.address))
            button.clicked.connect(lambda: self.root_path_selected.emit(recent))
            lt.addWidget(button)
        lt.addWidget(SepartorLine())

        lt.addSpacing(40)

        new_git_layout = QVBoxLayout()
        new_git_layout.addWidget(_title_label_('Clone Git Repository'))
        self.git_address.setPlaceholderText('git@github.com:wgryglas/reDocWriter.git')
        new_git_layout.addWidget(_make_form_row_('Git Address', self.git_address))

        self.local_path.setPlaceholderText('/home/user_name/Documentation/pelicanReDoc')
        self.open_loc_button.setFixedWidth(30)
        self.open_loc_button.setFixedHeight(30)
        new_git_layout.addWidget(_make_form_row_('Disk Location', self.local_path, self.open_loc_button))
        new_git_layout.setSizeConstraint(QLayout.SetMinimumSize)

        button_lt = QHBoxLayout()
        button_lt.addStretch(0)
        button_lt.addWidget(self.clone_button)

        new_git_layout.addLayout(button_lt)

        lt.addLayout(new_git_layout)

        lt.addStretch(50)

        outer = QHBoxLayout()
        outer.addStretch()
        outer.addLayout(lt)
        outer.addStretch()

        self.setLayout(outer)


class WelcomePanel(QWidget):

    on_ready = Signal()

    def __init__(self, system):
        QWidget.__init__(self)

        self.system = system

        lt = QVBoxLayout()

        title1 = QLabel('Welcome')
        title1.setAlignment(Qt.AlignCenter)
        f = title1.font()
        f.setPointSize(18)
        title1.setFont(f)
        title2 = QLabel('Do you want to create desktop shortcut?')
        title2.setAlignment(Qt.AlignCenter)

        yes = QPushButton('Yes')
        yes.clicked.connect(self.createShortcut)

        no = QPushButton('No')
        no.clicked.connect(self.createOnlyUserDir)

        btLt = QHBoxLayout()
        btLt.addStretch(0)
        btLt.addWidget(yes)
        btLt.addWidget(no)
        btLt.addStretch(0)

        lt.addStretch(0)
        lt.addWidget(title1)
        lt.addSpacing(10)
        lt.addWidget(title2)
        lt.addLayout(btLt)
        lt.addStretch(0)

        self.setLayout(lt)

    def createShortcut(self):
        self.system.createShortcut()
        self.system.createUserDir()
        self.on_ready.emit()

    def createOnlyUserDir(self):
        self.system.createUserDir()
        self.on_ready.emit()


class InitialPanel(QWidget):

    on_launcher_show = Signal()
    on_root_selection = Signal(str)
    on_settings_ready = Signal(object)

    def __init__(self, system, settings):
        QWidget.__init__(self)
        self.system = system
        self.settings = settings
        self.welcome = WelcomePanel(self.system)
        if system.isInitialized:
            self.configure_regular()
        else:
            self.configure_welcome()

    def loadSettings(self):
        self.settings.loadFromFile(self.system.settingsFilePath)
        self.on_settings_ready.emit(self.settings)

    def configure_regular(self):
        self.loadSettings()
        lt = QHBoxLayout()
        self.setLayout(lt)
        self.showLauncher()

    def configure_welcome(self):
        lt = QHBoxLayout()
        lt.addWidget(self.welcome)
        self.setLayout(lt)
        self.welcome.on_ready.connect(self.moveToLauncher)

    def moveToLauncher(self):
        self.loadSettings()

    def showLauncher(self):
        launcher = LauncherPanel(self.settings)
        launcher.root_path_selected.connect(self.on_root_selection.emit)
        self.layout().addWidget(launcher)
        self.welcome.hide()
        self.on_launcher_show.emit()




if __name__ == "__main__":
    import sys
    from app_settings import AppSettings

    app = QApplication(sys.argv)
    system = SystemSettings()
    panel = InitialPanel(system)
    panel.showMaximized()
    sys.exit(app.exec_())
