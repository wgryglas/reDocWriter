from pyqode.qt.QtCore import Signal, QSize, Qt, QTimer
from pyqode.qt.QtGui import QIcon
from pyqode.qt.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QFrame, QStyle
# use custom RstCodeEdit because could not install custom roles to work with linter
from code_edit import RstCodeEdit
from app_settings import ColorScheme


class EditorPanel(QWidget):
    content_changed = Signal()

    def __init__(self, settings):
        QWidget.__init__(self)

        self.settings = settings

        self.editor = RstCodeEdit(color_scheme='qt' if self.settings.color_scheme == ColorScheme.defualt else 'darcula')
        self.editor.setFrameStyle(QFrame.NoFrame)
        if self.settings.editor_font and len(self.settings.editor_font) > 0:
            self.editor.font_name = self.settings.editor_font

        self.text_modified = False
        self.editor.textChanged.connect(self._mark_modified_)

        self.undo = QPushButton()
        self.redo = QPushButton()

        self.content_update_timer = QTimer()
        self.content_update_timer.timeout.connect(self._check_content_change_)

        self._do_layout_()

    def configureButtons(self):
        self.undo.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        self.undo.setToolTip("Undo")
        self.undo.clicked.connect(lambda: self.editor.undo())

        self.redo.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        self.redo.setToolTip("Redo")
        self.redo.clicked.connect(lambda: self.editor.redo())

    def verticalScrollBar(self):
        return self.editor.verticalScrollBar()

    @property
    def plainText(self):
        return self.editor.toPlainText()

    @plainText.setter
    def plainText(self, content):
        self.editor.clear()
        self.editor.setPlainText(content)
        self._mark_modified_()

    @property
    def cursorColumn(self):
        return self.editor.textCursor().columnNumber()

    def insertText(self, text):
        self.editor.insertPlainText(text)
        self._mark_modified_()

    def insert_directive_in_current_position(self, text):
        # assert dictionary is placed in new line
        if self.cursorColumn > 0:
            text = '\n' + text
        self.insertText(text)

    def displayText(self, content):
        """
        display text just puts the text content, does not trigger
        content change event
        :param content: text to put in editor
        """
        self.editor.clear()
        self.editor.setPlainText(content)
        self.text_modified = False

    def _mark_modified_(self):
        """
        Triggers content change event. It is designed not
        to dispatch all change events but at certain rate.
        The content_changed signal can be attached to some
        external heavy renderer for processing sources
        """
        self.text_modified = True
        if not self.content_update_timer.isActive():
            self.content_update_timer.start(self.settings.content_refresh_time)

    def _check_content_change_(self):
        if self.text_modified:
            self.text_modified = False
            self.content_changed.emit()

    def _build_buttons_layout_(self):
        lt = QHBoxLayout()
        return lt

    def _do_layout_(self):
        lt = QVBoxLayout()
        lt.addLayout(self._build_buttons_layout_())
        lt.addWidget(self.editor)
        self.setLayout(lt)

