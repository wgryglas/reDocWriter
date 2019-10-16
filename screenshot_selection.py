from pyqode.qt.QtCore import Qt, QRect, QPoint, Signal, QTimer, QRegExp
from pyqode.qt.QtGui import QMainWindow, QPushButton, QStyle, QHBoxLayout, QVBoxLayout, QWidget, QCursor, QLabel, \
    QLineEdit, QIntValidator, QPainter, QColor, QPen, QComboBox, QRegExpValidator
from dialogs import OKCancelDialog
import icons


class Direction:
    left = 0
    top = 1
    right = 2
    bottom = 3


def makeHCenterLayout(widget):
    lt = QHBoxLayout()
    lt.addStretch(0)
    lt.addWidget(widget)
    lt.addStretch(0)
    return lt


class WindowRegionSelector(QMainWindow):
    on_quit = Signal()
    on_take_screenshot = Signal(object)

    def __init__(self, regions=dict(), showRect=None, gridSpcing=5, useGrid=True, hideOnClose=True):
        super(WindowRegionSelector, self).__init__()
        self.curr_dir = None
        self.press_pos = QPoint()
        self.startRect = QRect()
        self.useGrid = useGrid
        self.gridPixelSize = gridSpcing
        self.savedRegions = regions
        self.showRect = showRect
        self.hideOnClose = hideOnClose

        self.maximizeButton = QPushButton('Maximize')
        self.maximizeButton.clicked.connect(self.toggleFullScreen)

        def makeEdit(value):
            edit = QLineEdit(value)
            edit.returnPressed.connect(self.updateRectFromText)
            v = QIntValidator()
            v.setBottom(0)
            edit.setValidator(v)
            return edit

        self.xEdit = makeEdit('100')
        self.yEdit = makeEdit('100')
        self.wEdit = makeEdit('200')
        self.hEdit = makeEdit('100')
        self.editWidget = QWidget()

        self.takeScreenshot = QPushButton()
        self.takeScreenshot.setIcon(icons.get('screenshot'))
        self.takeScreenshot.setToolTip('Take screenshot now')
        self.takeScreenshot.clicked.connect(lambda: self.doScreenShot(0))

        delay = 5
        self.takeScreenshotDelayed = QPushButton()
        self.takeScreenshotDelayed.setIcon(icons.get('screenshot'))
        self.takeScreenshotDelayed.setToolTip('Take screenshot in {} seconds'.format(delay))
        self.takeScreenshotDelayed.setText('{} s'.format(delay))
        self.takeScreenshotDelayed.clicked.connect(lambda: self.doScreenShot(delay))

        self.namedRegionsSelector = QComboBox()
        self.namedRegionsSelector.addItem('Custom')
        for name in self.savedRegions:
            self.namedRegionsSelector.addItem(name)
        self.namedRegionsSelector.addItem('Save Current')
        self.namedRegionsSelector.currentIndexChanged.connect(self.handleNamedRegionSelection)
        self.initUI()

        self.updateTextFromRect()

    def doScreenShot(self, delay=0):
        r = self.currentRect()

        self.hide()

        def emitAndClose():
            self.on_take_screenshot.emit(r)
            if not self.hideOnClose:
                self.close()

        if delay == 0:
            emitAndClose()
        else:
            QTimer.singleShot(1000 * delay, emitAndClose)

    def grapMousePosAndRect(self):
        p = QCursor.pos()
        self.press_pos = p
        self.startRect.setRect(self.pos().x(), self.pos().y(), self.width(), self.height())

    def mouseReleaseEvent(self, QMouseEvent):
        self.releaseDir()

    def releaseDir(self):
        self.curr_dir = None

    def currentRect(self):
        return QRect(int(self.xEdit.text()), int(self.yEdit.text()),
                     int(self.wEdit.text()), int(self.hEdit.text()))

    def updateRectFromText(self):
        currR = self.rect()
        r = self.currentRect()

        if currR.width() != r.width() or currR.height() != r.height():
            self.resize(r.width(), r.height())

        if currR.x() != r.x() or currR.y() != r.y():
            self.move(r.x(), r.y())

        self.checkRegionNameIfMatch(r)

    def updateTextFromRect(self):
        p = self.pos()
        s = self.size()
        r = QRect(p.x(), p.y(), s.width(), s.height())
        self.xEdit.setText(str(r.x()))
        self.yEdit.setText(str(r.y()))
        self.wEdit.setText(str(r.width()))
        self.hEdit.setText(str(r.height()))
        self.checkRegionNameIfMatch(r)

    def checkRegionNameIfMatch(self, r):
        for name in self.savedRegions:
            reg = self.savedRegions[name]
            if reg == r:
                index = self.namedRegionsSelector.findText(name)
                if -1 < index != self.namedRegionsSelector.currentIndex():
                    self.namedRegionsSelector.setCurrentIndex(index)
                return
            else:
                print reg, r

        if self.namedRegionsSelector.currentIndex() != 0:
            self.namedRegionsSelector.setCurrentIndex(0)

    def snapCoordinate(self, c):
        rest = c % self.gridPixelSize
        result = (c / self.gridPixelSize) * self.gridPixelSize
        if rest > self.gridPixelSize / 2:
            result += self.gridPixelSize
        return result

    def constraint(self, rect):
        if self.useGrid:
            x = self.snapCoordinate(rect.x())
            y = self.snapCoordinate(rect.y())
            r = self.snapCoordinate(rect.right())
            b = self.snapCoordinate(rect.bottom())
            return QRect(x, y, r - x, b - y)
        else:
            return rect

    def mouseMoveEvent(self, QMouseEvent):
        p = QCursor.pos()
        result = QRect()
        if self.curr_dir == Direction.left or self.curr_dir == Direction.right:
            delta = p.x() - self.press_pos.x()
            if self.curr_dir == Direction.left:
                result.setRect(self.startRect.x() + delta, self.startRect.y(),
                               self.startRect.width() - delta, self.startRect.height())
            else:
                result.setRect(self.startRect.x(), self.startRect.y(),
                               self.startRect.width() + delta, self.startRect.height())

        elif self.curr_dir == Direction.top or self.curr_dir == Direction.bottom:
            delta = p.y() - self.press_pos.y()
            if self.curr_dir == Direction.top:
                result.setRect(self.startRect.x(), self.startRect.y() + delta,
                               self.startRect.width(), self.startRect.height() - delta)
            else:
                result.setRect(self.startRect.x(), self.startRect.y(),
                               self.startRect.width(), self.startRect.height() + delta)
        else:
            return

        result = self.constraint(result)

        self.xEdit.setText(str(result.x()))
        self.yEdit.setText(str(result.y()))
        self.wEdit.setText(str(result.width()))
        self.hEdit.setText(str(result.height()))
        self.updateRectFromText()

    def toggleFullScreen(self):
        if self.window().isMaximized():
            self.window().setWindowState(Qt.WindowNoState)
            self.maximizeButton.setText('Full Screen')
            self.editWidget.setVisible(True)
        else:
            #self.window().showMaximized()
            self.window().setWindowState(Qt.WindowMaximized)
            self.maximizeButton.setText('Part of Screen')
            self.editWidget.setVisible(False)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        qp.setPen(QColor(0, 0, 0))
        qp.drawRect(QRect(0, 0, self.width() - 1, self.height() - 1))

        qp.setPen(QPen(QColor(255, 255, 255), 1, Qt.DashLine))
        qp.drawRect(QRect(0, 0, self.width() - 1, self.height() - 1))

        qp.end()

    def handleNamedRegionSelection(self, index):
        if index == 0:
            return
        elif self.namedRegionsSelector.itemText(index) == 'Save Current':
            self.namedRegionsSelector.setCurrentIndex(0)
            self.openSaveRegionDialog()
        else:
            name = self.namedRegionsSelector.itemText(index)
            r = self.savedRegions[name]
            self.resize(r.width(), r.height())
            self.move(r.x(), r.y())
            self.updateTextFromRect()

    def savedCurrentRegion(self, name):
        r = self.currentRect()
        self.savedRegions[name] = r
        self.namedRegionsSelector.insertItem(1, name)
        self.checkRegionNameIfMatch(r)

    def openSaveRegionDialog(self):
        nameInput = QLineEdit()
        regex = '[A-Za-z0-9_]+'

        validator = QRegExpValidator(QRegExp(regex))
        nameInput.setValidator(validator)

        widget = QWidget()
        lt = QHBoxLayout()
        lt.addStretch()
        lt.addWidget(QLabel('Name'))
        lt.addWidget(nameInput)
        lt.addStretch()
        widget.setLayout(lt)

        d = OKCancelDialog(widget)
        d.setWindowTitle('Save Region as ...')
        d.setModal(True)

        d.on_ok.connect(lambda: self.savedCurrentRegion(nameInput.text()))

        p = self.pos()
        s = self.size()
        d.showNormal()
        d.move(p.x() + s.width() / 2 - d.width() / 2, p.y() + s.height() / 2 - d.height() / 2)

    def setPos(self, direction):
        self.curr_dir = direction

    def makeDirButton(self, direction, iconId):
        b = QPushButton()
        b.setObjectName('dir-button')
        b.pressed.connect(lambda: self.setPos(direction))
        b.pressed.connect(self.grapMousePosAndRect)
        b.setIcon(self.style().standardIcon(iconId))
        return b

    def show(self, *args, **kwargs):
        QMainWindow.show(self, *args, **kwargs)

        if self.showRect:
            self.resize(self.showRect.width(), self.showRect.height())
            self.move(self.showRect.x(), self.showRect.y())

        self.updateTextFromRect()

    def layoutEdits(self):
        def setSizes(widget):
            widget.setMaximumWidth(40)
            widget.setMaximumHeight(30)

        setSizes(self.xEdit)
        setSizes(self.yEdit)
        setSizes(self.wEdit)
        setSizes(self.hEdit)

        pos = QHBoxLayout()
        pos.setSpacing(0)
        pos.addWidget(QLabel('x'))
        pos.addSpacing(0)
        pos.addWidget(self.xEdit)
        pos.addSpacing(10)
        pos.addWidget(QLabel('y'))
        pos.addSpacing(0)
        pos.addWidget(self.yEdit)

        size = QHBoxLayout()
        size.setSpacing(0)
        size.setAlignment(Qt.AlignCenter)
        size.addWidget(QLabel('w'))
        size.addWidget(self.wEdit)
        size.addSpacing(10)
        size.addWidget(QLabel('h'))
        size.addWidget(self.hEdit)

        lt = QVBoxLayout()
        lt.setContentsMargins(0, 5, 0, 5)
        lt.addLayout(pos)
        lt.addLayout(size)
        lt.addWidget(self.namedRegionsSelector)

        self.editWidget.setStyleSheet("""
        
        """)
        self.editWidget.setLayout(lt)
        self.editWidget.setMaximumWidth(300)

    def initUI(self):
        mainStyle = """
           QWidget#screenshot-panel {
                background:rgba(255,255,255,80);
           }
           QPushButton {
             margin: 0px;
             margin-top:5px; margin-bottom:5px;
             padding: 3px;
             background: rgba(255, 255, 255, 200);
             border:none;
             color: black;
             border-radius:3px;
             outline:none;
             border: 1px solid darkgray;
           }
           QPushButton:hover {
               background: rgba(255, 255, 255, 255);
           }
           QPushButton#dir-button {
              margin: 0;
              padding: 3px;
              background:transparent;
              border:none;
              color: white;
              outline:none;
              border-radius:3px;
            }
            QPushButton#dir-button:hover {
                border: 1px solid darkgray;
                background:white;
            }
           QComboBox {
             margin: 0px;
             padding: 3px;
             background: rgba(255, 255, 255, 200);
             border:none;
             color: black;
             border-radius:3px;
             border: 1px solid darkgray;
           }
           QComboBox::drop-down {
             border: 0px solid black;
             border-left-width: 1px;
             border-left-color: darkgray;
             border-left-style: solid;
           }
           QComboBox::down-arrow {
             image:url(./assets/icons/arrow-down.png);
           }
           QComboBox:hover {
               background: rgba(255, 255, 255, 255);
           }
           QLabel {
                background: rgba(255, 255, 255, 200);
                padding: 0;
                padding-left:3px;
                padding-right:3px;
                margin: 0;
                color:black;
           }
           QLineEdit {
                background: rgba(255, 255, 255, 200);
                border:none;
                padding: 0;
                margin: 0;
                color:black;
           }
           QLineEdit:focus {
                background: rgba(255, 255, 255, 255);
           }
           """

        qbtn = QPushButton()
        qbtn.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        qbtn.setToolTip('Cancel')
        qbtn.clicked.connect(lambda: self.hide() if self.hideOnClose else self.close())
        qbtn.clicked.connect(self.on_quit.emit)
        qbtn.setMaximumWidth(35)
        qbtn.setMaximumHeight(35)
        self.maximizeButton.setMaximumHeight(35)

        left = self.makeDirButton(Direction.left, QStyle.SP_ArrowBack)
        right = self.makeDirButton(Direction.right, QStyle.SP_ArrowForward)
        top = self.makeDirButton(Direction.top, QStyle.SP_ArrowUp)
        bottom = self.makeDirButton(Direction.bottom, QStyle.SP_ArrowDown)

        headerLt = QHBoxLayout()
        headerLt.setContentsMargins(0, 0, 0, 0)
        headerLt.setSpacing(5)
        headerLt.addWidget(self.maximizeButton)
        headerLt.addWidget(qbtn)

        centralLt = QVBoxLayout()
        centralLt.addLayout(headerLt)
        self.layoutEdits()
        centralLt.addLayout(makeHCenterLayout(self.editWidget))

        buttonsLt = QHBoxLayout()
        buttonsLt.setContentsMargins(0, 0, 0, 0)
        buttonsLt.setSpacing(5)
        buttonsLt.addWidget(self.takeScreenshot)
        buttonsLt.addWidget(self.takeScreenshotDelayed)
        centralLt.addLayout(buttonsLt)

        ltLeftRight = QHBoxLayout()
        ltLeftRight.setSpacing(0)
        ltLeftRight.setContentsMargins(0, 0, 0, 0)
        ltLeftRight.addWidget(left)
        ltLeftRight.addStretch(10)
        ltLeftRight.addLayout(centralLt)
        ltLeftRight.addStretch(10)
        ltLeftRight.addWidget(right)

        vertLt = QVBoxLayout()
        vertLt.setContentsMargins(0, 0, 0, 0)
        vertLt.setSpacing(0)
        vertLt.addLayout(makeHCenterLayout(top))
        vertLt.addStretch(10)
        vertLt.addLayout(ltLeftRight)
        vertLt.addStretch(10)
        vertLt.addLayout(makeHCenterLayout(bottom))

        mainWidget = QWidget()
        mainWidget.setContentsMargins(0, 0, 0, 0)
        mainWidget.setLayout(vertLt)
        mainWidget.setObjectName('screenshot-panel')

        self.setStyleSheet(mainStyle)
        self.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(mainWidget)
        self.setWindowTitle('Screenshot selection')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)