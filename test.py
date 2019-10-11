

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
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QRect, QPoint
from PyQt4.QtGui import QPushButton, QStyle, QHBoxLayout, QVBoxLayout, QWidget, QCursor, QApplication

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


class WindowRegionSelector(QtGui.QMainWindow):
    def __init__(self):
        super(WindowRegionSelector, self).__init__()
        self.initUI()

        self.curr_dir = None
        self.press_pos = QPoint()
        self.startRect = QRect()
        self.useGrid = True
        self.gridPixelSize = 10

    def grapMousePosAndRect(self):
        p = QCursor.pos()
        self.press_pos = p
        print self.pos()
        self.startRect.setRect(self.pos().x(), self.pos().y(), self.width(), self.height())

    def mouseReleaseEvent(self, QMouseEvent):
        self.releaseDir()

    def releaseDir(self):
        self.curr_dir = None

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
        self.resize(result.width(), result.height())
        self.move(result.x(), result.y())

    def makeFullScreen(self):
        # self.window().setWindowFlags(Qt.WindowMaximized)
        self.window().showMaximized()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QColor(255, 255, 255))
        qp.drawRect(QRect(0, 0, self.width()-1, self.height()-1))
        qp.end()

    def setPos(self, dir):
        print 'setting dir', dir
        self.curr_dir = dir

    def makeDirButton(self, dir, iconId, style):
        b = QPushButton()
        if style:
            b.setStyleSheet(style)
        b.pressed.connect(lambda: self.setPos(dir))
        b.pressed.connect(self.grapMousePosAndRect)
        b.setIcon(self.style().standardIcon(iconId))
        return b

    def initUI(self):
        transp_button_style = """
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

        qbtn = QPushButton('Quit')
        qbtn.clicked.connect(lambda: self.close())

        maximize = QPushButton('Maximize')
        maximize.clicked.connect(self.makeFullScreen)

        left = self.makeDirButton(Direction.left, QStyle.SP_ArrowBack, transp_button_style)
        right = self.makeDirButton(Direction.right, QStyle.SP_ArrowForward, transp_button_style)
        top = self.makeDirButton(Direction.top, QStyle.SP_ArrowUp, transp_button_style)
        bottom = self.makeDirButton(Direction.bottom, QStyle.SP_ArrowDown, transp_button_style)

        ltLeftRight = QHBoxLayout()
        ltLeftRight.setSpacing(0)
        ltLeftRight.setContentsMargins(0, 0, 0, 0)
        ltLeftRight.addWidget(left)
        ltLeftRight.addStretch(10)
        ltLeftRight.addWidget(qbtn)
        ltLeftRight.addWidget(maximize)
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

        # self.setGeometry(0, 0, 1024, 768)
        # self.setWindowTitle('Quit button')
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()



def main():
    app = QtGui.QApplication(sys.argv)
    ex = WindowRegionSelector()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()