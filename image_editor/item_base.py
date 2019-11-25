from pyqode.qt.QtWidgets import QGraphicsItem, QPen, QColor, QPainter, QPainterPath


class ItemBase(QGraphicsItem):
    def __init__(self, styles):
        QGraphicsItem.__init__(self)
        self._isEdited_ = False
        self._isDragged_ = False
        self._styles_ = styles

    def getStyle(self):
        return self._styles_.get(self)

    def isEdited(self):
        return self._isEdited_

    def setEdited(self, flag):
        self._isEdited_ = flag
        self.paint()

    def isEditable(self):
        return False

    def isDragged(self):
        return self._isDragged_

    def setDragged(self, value):
        self._isDragged_ = value
