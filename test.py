

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
from PyQt4.QtCore import Qt, QRect
from PyQt4.QtGui import QPushButton

class Example(QtGui.QMainWindow):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def mousePressEvent(self, QMouseEvent):
        print QMouseEvent.pos()

    def mouseReleaseEvent(self, QMouseEvent):
        cursor = QtGui.QCursor()
        print cursor.pos()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QColor(255, 255, 255))
        qp.drawRect(QRect(0, 0, self.width()-1, self.height()-1))
        qp.end()


    def setLeft(self):
        pass


    def initUI(self):
        qbtn = QtGui.QPushButton('Quit', self)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)
        qbtn.clicked.connect(lambda : self.close())

        left = QPushButton()
        # left.pressed.con


        self.setGeometry(0, 0, 1024, 768)
        self.setWindowTitle('Quit button')
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()

    def test(self):
        print "test"


def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()