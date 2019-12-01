from pyqode.qt.QtCore import Qt, QSizeF, QRectF, QPointF, Signal
from pyqode.qt.QtWidgets import QPen, QPainter, QColor

from item_base import ItemBase
from handle_itemes import ExtensionArrow, MoveHandle
from item_style import ItemStyles, GraphicsStyle
from number_item import AnchoredNumberItem
from rect_postion import CornerPosition


def makeStyles():
    styles = ItemStyles(border_color=ItemStyles.markColor)
    return styles


class RectSelectionItem(ItemBase):
    def __init__(self, size, constr, style=makeStyles()):
        ItemBase.__init__(self, style)
        self.setFreeMovable(False)

        self.setFlag(ItemBase.ItemIsSelectable)
        self.size = size
        self.constr = constr

        self.setAcceptHoverEvents(True)

        down = ExtensionArrow('down', lambda v: self.setRect(self.x, self.y, self.width, self.height+v))
        down.setParentItem(self)

        up = ExtensionArrow('up', lambda v: self.setRect(self.x, self.y-v, self.width, self.height+v))
        up.setParentItem(self)

        left = ExtensionArrow('left', lambda v: self.setRect(self.x-v, self.y, self.width+v, self.height))
        left.setParentItem(self)

        right = ExtensionArrow('right', lambda v: self.setRect(self.x, self.y, self.width+v, self.height))
        right.setParentItem(self)

        self.posHandle = MoveHandle(lambda delta, sugessted: self.setPos(self.constr(self.pos() + delta)))
        self.posHandle.setParentItem(self)

        self.arrows = [left, right, up, down]
        self.setRect(0, 0, size.width(), size.height())

        self.activeItems = [self.posHandle]
        self.activeItems.extend(self.arrows)

        for a in self.activeItems:
            a.setVisible(False)

    def isEditable(self):
        return True

    def setEdited(self, flag):
        ItemBase.setEdited(self, flag)
        for e in self.activeItems:
            e.setVisible(flag)
        if flag:
            self.setFlag(ItemBase.ItemIsSelectable, False)
        else:
            self.setFlag(ItemBase.ItemIsSelectable, True)

    def dragUp(self, v):
        p = self.pos()
        self.setPos(p.x(), p.y() - v)
        self.setSize(self.width, self.height + v)

    def dragLeft(self, v):
        p = self.pos()
        self.setSize(self.width+v, self.height)
        self.setPos(p.x() - v, p.y())
        # self.setRect()

    def dragRight(self, v):
        self.setSize(self.width+v, self.height)

    def setRect(self, x, y, w, h):
        # if self.x == x and self.y == y and self.width == w and self.height == h:
        #     return
        if w <= 0:
            w = self.width

        if h <= 0:
            h = self.height

        # self.arrows[0].setPos(0, (h-self.arrows[0].rect().height())/2 )
        # self.arrows[1].setPos(w, (h-self.arrows[1].rect().height())/2 )
        # self.arrows[2].setPos((w-self.arrows[2].rect().width())/2, 0)
        # self.arrows[3].setPos((w-self.arrows[3].rect().width())/2, h)
        self.arrows[0].setPos(0, h/2)
        self.arrows[1].setPos(w, h/2)
        self.arrows[2].setPos(w/2, 0)
        self.arrows[3].setPos(w/2, h)

        min = self.constr(QPointF(x, y))
        max = self.constr(QPointF(x+w, y+h))

        self.size = QSizeF(max.x()-min.x(), max.y()-min.y())

        self.posHandle.setPos(self.size.width()/2, self.size.height()/2)

        x = min.x()
        y = min.y()

        #force redraw by chaning position
        if self.x == x and self.y == y:
            self.setPos(x-1, y-1)
            self.setPos(x, y)
        else:
            self.setPos(x, y)

    @property
    def x(self):
        return self.pos().x()

    @property
    def y(self):
        return self.pos().y()

    @property
    def width(self):
        return self.size.width()

    @property
    def height(self):
        return self.size.height()

    def boundingRect(self, *args, **kwargs):
        return QRectF(0, 0, self.size.width(), self.size.height())

    def paintBorder(self, qPainter):
        qPainter.drawRect(0, 0, self.width, self.height)

    def paintBackground(self, qPainter):
        qPainter.fillRect(0, 0, self.width, self.height)

    def isAnyElementSelected(self):
        sel = self.isSelected()
        if not sel:
            sel = any([a.isSelected() for a in self.activeItems])
        return sel

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        qPainter.setRenderHint(QPainter.Antialiasing, True)
        qPainter.setRenderHint(QPainter.TextAntialiasing, True)

        s = self.getStyle()
        if s.background_color:
            s.configure(qPainter, GraphicsStyle.BACKGROUND)
            self.paintBackground(qPainter)

        if s.border_color:
            s.configure(qPainter, GraphicsStyle.BORDER)
            self.paintBorder(qPainter)

        # force redraw on child selection changed (no need now, currently update on mouse move)
        # if need_redraw:
        #     # self.update(self.boundingRect())
        #     p = self.pos()
        #     self.setPos(p.x()-1, p.y()-1)
        #     self.setPos(p.x(), p.y())

    def dragMove(self, delta, suggestedPosition):
        self.setPos(self.constr(self.pos() + delta))

    def clone(self):
        item = RectSelectionItem(self.size, self.constr)
        item.setPos(self.x, self.y)
        return item


def makeEllipseStyles():
    styles = ItemStyles(border_color=ItemStyles.markColor, antialiased=True)
    return styles


class EllipseSelectionItem(RectSelectionItem):
    def __init__(self, size, constr, style=makeEllipseStyles()):
        RectSelectionItem.__init__(self, size, constr, style)

    def paintBackground(self, qPainter):
        qPainter.fillElipse(0, 0, self.width, self.height)

    def paintBorder(self, qPainter):
        qPainter.drawEllipse(0, 0, self.width, self.height)

    def clone(self):
        item = EllipseSelectionItem(self.size, self.constr)
        item.setPos(self.x, self.y)
        return item


def makeNumberStyle():
    styles = ItemStyles(background_color=ItemStyles.markColor, antialiased=True)
    styles.set_style('select', background_color=ItemStyles.markColor)
    return styles


class RectNumberedItem(RectSelectionItem):
    def __init__(self, size, constr, numberProvider):
        RectSelectionItem.__init__(self, size, constr)
        self.number = AnchoredNumberItem(numberProvider, constr, self.positionNumber, style=makeNumberStyle())
        self.number.setParentItem(self)
        self.activeShift = 0
        self.numberShift = -5
        self.positionNumber()

    def setSelected(self, flag):
        if flag:
            self.number.setSelected(True)
        RectSelectionItem.setSelected(self, flag)

    def paintBorder(self, qPainter):
        RectSelectionItem.paintBorder(self, qPainter)

    def setEdited(self, flag):
        RectSelectionItem.setEdited(self, flag)
        self.activeNumber(flag)

    def positionNumber(self):
        s = self.activeShift + self.numberShift
        if self.number.corner == CornerPosition.top_left:
            self.number.setPos(-self.number.size-s, -self.number.size-s)
        elif self.number.corner == CornerPosition.top_right:
            self.number.setPos(self.width+s, -self.number.size-s)
        elif self.number.corner == CornerPosition.bottom_left:
            self.number.setPos(-self.number.size-s, self.height+s)
        else:
            self.number.setPos(self.width+s, self.height+s)

        if self.scene():
            self.scene().update()

    def activeNumber(self, apart):
        self.activeShift = 0 if not apart else self.number.size / 2
        self.positionNumber()

        # #force redraw
        # self.setPos(self.x-1, self.y-1)
        # self.setPos(self.x+1, self.y+1)
        # TODO scene updates on any mouse move
        # self.scene().update()

    def clone(self):
        item = RectNumberedItem(self.size, self.constr, self.number.numberProvider)
        item.setPos(self.x, self.y)
        return item
