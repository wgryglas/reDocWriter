

from git_repository import GitRepository
from core import Session

# repo = GitRepository("/home/wgryglas/Code/Python/pelicanReDoc")
# repo = GitRepository("/home/wgryglas/python/pelicanDoc")

# print repo.isModified()

# print repo.root_path


# session = Session(repo)
#
# print session._to_local_src_path_('/home/wgryglas/python/pelicanDoc/content/test.rst')

# session.set_active_file('test.rst')

# session.update_website()

# session.start_local_server()

#print session.get_sources_structure()


#root = session.get_sources_structure()

#local_images = session._env_.get_figures_folder_path_for('test.rst')

#print root.find_folder_by_path(session._env_.source_full_path(local_images))

# print repo.isRemoteUpToDate()

# from app_settings import AppSettings
# settings = AppSettings()
# # settings.set('figure_width', '500 px')
# # settings.saveToFile('/home/wgryglas/test_settings.xml')
# # settings.loadFromFile('/home/wgryglas/test_settings.xml')
#
# print settings.recent, settings.figure_width, settings.sort_images, settings.editor_font
#
# from app_settings import SystemSettings
#
# sys = SystemSettings()
#
# print sys.userSettingsDir, sys.settingsFilePath, sys.some_prop

# from file_templates import emptyFileTemplate
# print session.substituteTemplatText(emptyFileTemplate(), '/home/wgryglas/python/pelicanDoc/content/test.rst')



# import sys
# from PyQt4 import QtGui, QtCore
# from PyQt4.QtCore import Qt
#
# class MyView(QtGui.QGraphicsView):
#     def __init__(self):
#         QtGui.QGraphicsView.__init__(self)
#
#         self.setStyleSheet("background:transparent;")
#
#         self.setGeometry(QtCore.QRect(100, 100, 600, 250))
#
#         self.scene = QtGui.QGraphicsScene(self)
#         self.scene.setSceneRect(QtCore.QRectF())
#
#         self.setScene(self.scene)
#
#         for i in range(5):
#             self.item = QtGui.QGraphicsEllipseItem(i*75, 10, 60, 40)
#             self.scene.addItem(self.item)
#
#
#     def eventFilter(self, source, event):
#         if event.type() == QtCore.QEvent.MouseMove:
#             if event.buttons() == QtCore.Qt.NoButton:
#                 pos = event.pos()
#                 #.setText('x: %d, y: %d' % (pos.x(), pos.y()))
#                 print pos.x(), pos.y()
#             else:
#                 pass  # do other stuff
#         return QtGui.QMainWindow.eventFilter(self, source, event)
#
#
# if __name__ == '__main__':
#     app = QtGui.QApplication(sys.argv)
#     view = MyView()
#     # view.setAttribute(Qt.WA_NoSystemBackground, True)
#     # view.setAttribute(Qt.WA_OpaquePaintEvent, False)
#     # view.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
#     # view.setAutoFillBackground(False)
#     view.setAttribute(Qt.WA_TranslucentBackground)
#     view.show()
#     sys.exit(app.exec_())

import sys
from pyqode.qt.QtCore import Qt, QRect, QPoint, Signal, QTimer, QRegExp
from pyqode.qt.QtGui import QMainWindow, QPushButton, QStyle, QHBoxLayout, QVBoxLayout, QWidget, QCursor, QLabel, \
    QLineEdit, QIntValidator, QApplication, QPainter, QColor, QPen, QComboBox, QDialog, QRegExpValidator
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
    on_take_screenshot = Signal(int, int, int, int)

    def __init__(self, regions=dict(), gridSpcing=5, useGrid=True):
        super(WindowRegionSelector, self).__init__()
        self.curr_dir = None
        self.press_pos = QPoint()
        self.startRect = QRect()
        self.useGrid = useGrid
        self.gridPixelSize = gridSpcing
        self.savedRegions = regions

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
        if delay == 0:
            self.on_take_screenshot.emit(r.x(), r.y(), r.width(), r.height())
        else:
            QTimer.singleShot(1000*delay, lambda: self.on_take_screenshot.emit(r.x(), r.y(), r.width(), r.height()))

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
        print 'checking'
        for name in self.savedRegions:
            reg = self.savedRegions[name]
            if reg == r:
                index = self.namedRegionsSelector.findText(name)
                print 'matching', name, index
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
            return QRect(x, y, r-x, b - y)
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
                               self.startRect.width(),  self.startRect.height() + delta)
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
            self.window().showNormal()
            self.maximizeButton.setText('Full Screen')
            self.editWidget.setVisible(True)
            # self.updateTextFromRect()
        else:
            self.window().showMaximized()
            self.maximizeButton.setText('Part of Screen')
            self.editWidget.setVisible(False)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        qp.setPen(QColor(0, 0, 0))
        qp.drawRect(QRect(0, 0, self.width() - 1, self.height() - 1))

        qp.setPen(QPen(QColor(255, 255, 255), 1, Qt.DashLine))
        # qp.setPen(QColor(255, 255, 255))
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
            print 'loading', r
            self.resize(r.width(), r.height())
            self.move(r.x(), r.y())
            self.updateTextFromRect()

    def savedCurrentRegion(self, name):
        r = self.currentRect()
        self.savedRegions[name] = r
        self.namedRegionsSelector.insertItem(1, name)

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
        d.showNormal()

        d.on_ok.connect(lambda: self.savedCurrentRegion(nameInput.text()))


    def setPos(self, direction):
        self.curr_dir = direction

    def makeDirButton(self, direction, iconId, style):
        b = QPushButton()
        if style:
            b.setStyleSheet(style)
        b.pressed.connect(lambda: self.setPos(direction))
        b.pressed.connect(self.grapMousePosAndRect)
        b.setIcon(self.style().standardIcon(iconId))
        return b

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
        pos.addSpacing(20)
        pos.addWidget(QLabel('y'))
        pos.addSpacing(0)
        pos.addWidget(self.yEdit)

        size = QHBoxLayout()
        size.setSpacing(0)
        size.setAlignment(Qt.AlignCenter)
        size.addWidget(QLabel('w'))
        size.addWidget(self.wEdit)
        size.addSpacing(20)
        size.addWidget(QLabel('h'))
        size.addWidget(self.hEdit)

        lt = QVBoxLayout()
        lt.addLayout(pos)
        lt.addLayout(size)

        self.editWidget.setStyleSheet("""
        QLabel {
            background: rgba(140, 180, 255, 127);;
            padding: 0;
            margin: 0;
        }
        QLineEdit {
            background: rgba(140, 180, 255, 127);;
            border:none;
            padding: 0;
            margin: 0;
        }
        QLineEdit:focus {
            background: rgba(140, 180, 255, 200);;
            border:none;
            padding: 0;
            margin: 0;
        }
        
        """)
        self.editWidget.setLayout(lt)
        self.editWidget.setMaximumWidth(300)

    def initUI(self):
        dir_button_style = """
        QPushButton {
          margin: 0;
          padding: 0;
          background:transparent;
          border:none;
          color: white;
        }
        QPushButton:hover {
            border: 1px solid white;
            border-radius:3px;
        }
        """
        in_button_style = """
        QPushButton {
          margin: 5px;
          padding: 3px;
          background:rgba(140, 180, 255, 127);
          border:none;
          color: black;
          border-radius:3px;
        }
        QPushButton:hover {
            border: 1px solid rgb(100, 140, 200);
            background:rgba(140, 180, 255, 200);
        }
        QComboBox {
          margin: 5px;
          padding: 3px;
          background:rgba(140, 180, 255, 127);
          border:none;
          color: black;
          border-radius:3px;
        }
        QComboBox:hover {
            border: 1px solid rgb(100, 140, 200);
            background:rgba(140, 180, 255, 200);
        }
        """

        self.setStyleSheet(in_button_style)

        qbtn = QPushButton()
        qbtn.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        qbtn.setToolTip('Cancel')
        qbtn.clicked.connect(lambda: self.close())
        qbtn.setMaximumWidth(35)
        qbtn.setMaximumHeight(35)
        self.maximizeButton.setMaximumHeight(35)

        left = self.makeDirButton(Direction.left, QStyle.SP_ArrowBack, dir_button_style)
        right = self.makeDirButton(Direction.right, QStyle.SP_ArrowForward, dir_button_style)
        top = self.makeDirButton(Direction.top, QStyle.SP_ArrowUp, dir_button_style)
        bottom = self.makeDirButton(Direction.bottom, QStyle.SP_ArrowDown, dir_button_style)

        headerLt = QHBoxLayout()
        headerLt.addWidget(self.maximizeButton)
        headerLt.addWidget(qbtn)

        centralLt = QVBoxLayout()
        centralLt.addLayout(headerLt)
        self.layoutEdits()
        centralLt.addLayout(makeHCenterLayout(self.editWidget))
        centralLt.addWidget(self.namedRegionsSelector)
        centralLt.addWidget(self.takeScreenshot)
        centralLt.addWidget(self.takeScreenshotDelayed)

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

        self.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(mainWidget)

        self.setWindowTitle('Screenshot selection')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)


def main():
    app = QApplication(sys.argv)
    ex = WindowRegionSelector()
    ex.show()
    ex.openSaveRegionDialog()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()