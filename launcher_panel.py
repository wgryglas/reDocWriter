from pyqode.qt.QtCore import *
from pyqode.qt.QtWidgets import *
from cusotm_widgets import LinkLikeButton, SepartorLine

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


class StartPanel(QWidget):
    pass


class InitializePanel(QWidget):
    pass



if __name__ == "__main__":
    import sys
    from app_settings import AppSettings

    app = QApplication(sys.argv)
    panel = LauncherPanel(AppSettings())
    panel.show()
    sys.exit(app.exec_())
