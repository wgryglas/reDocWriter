from pyqode.qt.QtCore import Qt, QSizeF, QRectF, QPointF, Signal
from pyqode.qt.QtWidgets import QPen, QPainter, QColor, QPainterPath

from item_base import ItemBase
from handle_itemes import ExtensionArrow, MoveHandle
from item_style import ItemStyles, GraphicsStyle
from number_item import AnchoredNumberItem
from enums import RectAnchors
from properties import FloatProperty


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

        down = ExtensionArrow('down', lambda: self.height, lambda v: self.setRect(self.x, self.y, self.width, v))
        down.setParentItem(self)

        up = ExtensionArrow('up', lambda: self.height, lambda v: self.setRect(self.x, self.y+self.height-v, self.width, v))
        up.setParentItem(self)

        left = ExtensionArrow('left', lambda: self.width, lambda v: self.setRect(self.x+self.width-v, self.y, v, self.height))
        left.setParentItem(self)

        right = ExtensionArrow('right', lambda: self.width, lambda v: self.setRect(self.x, self.y, v, self.height))
        right.setParentItem(self)

        self.posHandle = MoveHandle(lambda: self.pos(), lambda pos: self.setPos(self.constr(pos)))
        self.posHandle.setParentItem(self)

        self.arrows = [left, right, up, down]
        self.setRect(0, 0, size.width(), size.height())

        self.activeItems = [self.posHandle]
        self.activeItems.extend(self.arrows)

        for a in self.activeItems:
            a.setVisible(False)

        self._properties_.set([FloatProperty('x', lambda v: self.setPos(v, self.y), lambda: self.x),
                               FloatProperty('y', lambda v: self.setPos(self.x, v), lambda: self.y),
                               FloatProperty('width', lambda v: self.setRect(self.x, self.y, v, self.height), lambda: self.width),
                               FloatProperty('height', lambda v: self.setRect(self.x, self.y, self.width, v), lambda: self.height)])

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

    def setConstrainedPosition(self, rawPoint):
        pnt = self.constr(rawPoint)
        self.setPos(pnt.x(), pnt.y())

    def setRect(self, x, y, w, h):
        # if self.x == x and self.y == y and self.width == w and self.height == h:
        #     return
        if w <= 0 or h <= 0:
            return

        min = self.constr(QPointF(x, y))
        max = self.constr(QPointF(x+w, y+h))

        self.size = QSizeF(max.x()-min.x(), max.y()-min.y())

        self.arrows[0].setPos(0, self.height / 2)
        self.arrows[1].setPos(self.width, self.height / 2)
        self.arrows[2].setPos(self.width / 2, 0)
        self.arrows[3].setPos(self.width / 2, self.height)

        self.posHandle.setPos(self.size.width()/2, self.size.height()/2)

        x = min.x()
        y = min.y()

        # #force redraw by chaning position
        # if self.x == x and self.y == y:
        #     self.setPos(x-1, y-1)
        #     self.setPos(x, y)
        # else:
        self.setPos(x, y)

        self._properties_.changed.emit()

    def setPos(self, *args):
        ItemBase.setPos(self, *args)
        self._properties_.changed.emit()

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
        # w = self.getStyle().width
        # return QRectF(-w, -w, self.width+w, self.height+w)
        return QRectF(0, 0, self.width, self.height)

    def paintBorder(self, qPainter, st):
        w = float(st.width)
        rect = QPainterPath()
        rect.addRect(-w/2, -w/2, self.width+w, self.height+w)
        qPainter.drawPath(rect)

    def paintBackground(self, qPainter):
        qPainter.fillRect(0, 0, self.width, self.height)

    def isAnyElementSelected(self):
        sel = self.isSelected()
        if not sel:
            sel = any([a.isSelected() for a in self.activeItems])
        return sel

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):

        qPainter.save()

        # qPainter.setRenderHint(QPainter.Antialiasing, True)
        # qPainter.setRenderHint(QPainter.TextAntialiasing, True)
        s = self.getStyle()
        if s.background_color:
            s.configure(qPainter, GraphicsStyle.BACKGROUND)
            self.paintBackground(qPainter)

        if s.border_color:
            s.configure(qPainter, GraphicsStyle.BORDER)
            self.paintBorder(qPainter, s)

        # force redraw on child selection changed (no need now, currently update on mouse move)
        # if need_redraw:
        #     # self.update(self.boundingRect())
        #     p = self.pos()
        #     self.setPos(p.x()-1, p.y()-1)
        #     self.setPos(p.x(), p.y())
        qPainter.restore()

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

    def paintBorder(self, qPainter, st):
        w = float(st.width)/2
        path = QPainterPath()
        path.addEllipse(-w, -w, self.width + 2*w, self.height + 2*w)
        qPainter.drawPath(path)

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
        self.number = AnchoredNumberItem(numberProvider, constr, self.positionNumber, lambda: self.boundingRect().size(), style=makeNumberStyle())
        self.activeShift = 0
        self.borderWidth = 3
        RectSelectionItem.__init__(self, size, constr)
        self.number.setParentItem(self)
        self.positionNumber()

        from properties import IntProperty
        self.properties().append(IntProperty('Number', lambda v: self.number.setNunber(v), lambda: self.number.number))

    def setSelected(self, flag):
        if flag:
            self.number.setSelected(True)
        RectSelectionItem.setSelected(self, flag)

    def setEdited(self, flag):
        RectSelectionItem.setEdited(self, flag)
        self.activeNumber(flag)

    def setRect(self, x, y, w, h):
        RectSelectionItem.setRect(self, x, y, w, h)
        self.positionNumber()

    def positionNumber(self):
        from numpy import sqrt
        rect = self.boundingRect()
        ins = self.borderWidth
        rect.setRect(rect.x()-ins-1.5, rect.y()-ins-1.5,
                     rect.width()+2*ins, rect.height()+2*ins)
        pos = RectAnchors.positionOnRect(rect, self.number.corner)
        dir = RectAnchors.outDir(self.number.corner)
        s = self.activeShift + self.number.size / 2
        self.number.setPos(pos.x() + dir.x()*s, pos.y() + dir.y()*s)

        #
        # if self.number.corner == CornerPosition.top_left:
        #     self.number.setPos(-self.number.size-s, -self.number.size-s)
        # elif self.number.corner == CornerPosition.top_right:
        #     self.number.setPos(self.width+s, -self.number.size-s)
        # elif self.number.corner == CornerPosition.bottom_left:
        #     self.number.setPos(-self.number.size-s, self.height+s)
        # else:
        #     self.number.setPos(self.width+s, self.height+s)
        # if self.scene():
        #     self.scene().update()

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
