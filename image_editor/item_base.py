from pyqode.qt.QtWidgets import QGraphicsItem


class ItemBase(QGraphicsItem):
    def __init__(self, styles):
        QGraphicsItem.__init__(self)
        self._isEdited_ = False
        self._isDragged_ = False
        self._isMovable_ = True
        self._styles_ = styles

    def getStyle(self):
        return self._styles_.get(self)

    def isEdited(self):
        return self._isEdited_

    def setEdited(self, flag):
        self._isEdited_ = flag

    def isEditable(self):
        return False

    def isDragged(self):
        return self._isDragged_

    def setFreeMovable(self, flag):
        self._isMovable_ = flag

    def isFreeMovable(self):
        return self._isMovable_

    def setDragged(self, value):
        self._isDragged_ = value

    def isConstantSize(self):
        return False

    def setSizeScale(self, scale):
        pass

    def dragMove(self, localDelta, totalDelta):
        pass
