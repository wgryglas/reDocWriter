
from pyqode.qt.QtCore import Qt, QSizeF, QRectF, QPointF, Signal

from pyqode.qt.QtWidgets import QGraphicsItem, QPen, QColor, QPainter, QPainterPath, QGraphicsRectItem, \
    QGraphicsPixmapItem, QPixmap

from item_style import ItemStyles, GraphicsStyle
from item_base import ItemBase


def makeArrowStyle():
    styles = ItemStyles(background_color=QColor(100, 136, 255, 100))
    styles.set_style('hover', border_color=ItemStyles.hoverColor)
    styles.set_style('select', background_color=QColor(100, 136, 255, 100))
    return styles


class ExtensionArrow(ItemBase):
    def __init__(self, orientation, on_drag, style=makeArrowStyle()):
        ItemBase.__init__(self, style)
        image = QGraphicsPixmapItem(QPixmap('/home/wgryglas/Code/Python/reDocsEditor/assets/icons/arrow-down.png'))
        image.setParentItem(self)
        self.on_drag = on_drag
        self._rect_ = QRectF(0, 0, 0, 0)

        if orientation == 'up':
            self.setRect(QRectF(0, -22, 30, 15))
            image.rotate(180)
            image.setPos(24, -5)
        elif orientation == 'down':
            self.setRect(QRectF(0, 5, 30, 15))
            image.setPos(8, 5)
        elif orientation == 'left':
            self.setRect(QRectF(-22, 0, 15, 30))
            image.rotate(90)
            image.setPos(-5, 8)
        else:
            self.setRect(QRectF(5, 0, 15, 30))
            image.rotate(-90)
            image.setPos(5, 24)

        # self.setBrush(QColor(100, 136, 255, 100))
        # self.setPen(QColor(100, 136, 255, 100))

        self.orientation = orientation

        image.setFlag(QGraphicsItem.ItemIsSelectable, False)

        self.image = image

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setAcceptHoverEvents(True)

        # self.setFlag(QGraphicsItem.ItemIsFocusable)

    def setRect(self, rect):
        self._rect_ = rect

    def rect(self):
        return self._rect_

    def boundingRect(self, *args, **kwargs):
        return self._rect_

    def _paint_rect_(self):
        return self._rect_
        #return QRectF(self._rect_.x(), self._rect_.y(), self._rect_.width()+1, self._rect_.height()+1)

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        # qPainter.fillRect(2, 2, 28, 18, QColor(100, 136, 255, 100))

        style = self.getStyle()

        # if self.isUnderMouse() or self.image.isUnderMouse():
        #     self.setBrush()
        # else:
        #     self.setBrush(QColor(100, 136, 255, 100))
        if style.background_color:
            qPainter.setPen(style.background_color)
            qPainter.fillRect(self._rect_, style.background_color)

        if style.border_color:
            qPainter.setPen(style.border_color)
            qPainter.drawRect(self._paint_rect_())

            # qPainter.drawPath(path, style.border_color)

        #QGraphicsRectItem.paint(self, qPainter, qStyleOptionGraphicsItem, qWidget)



    def dragMove(self, delta, suggestedPosition):
        if self.orientation == 'up':
            self.on_drag(-delta.y())
        elif self.orientation == 'down':
            self.on_drag(delta.y())
        elif self.orientation == 'left':
            self.on_drag(-delta.x())
        else:
            self.on_drag(delta.x())


def makeHandleStyle():
    styles = ItemStyles(background_color=ItemStyles.markColor)
    styles.set_style('hover', background_color=ItemStyles.hoverColor)
    return styles


class MoveHandle(ItemBase):

    def __init__(self, on_drag, w=12, h=12, style=None):
        ItemBase.__init__(self, style if style else makeHandleStyle())
        self.w = w
        self.h = h
        self.on_drag = on_drag
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        # self.setFlag(QGraphicsItem.ITem)
        self.setAcceptHoverEvents(True)

    def boundingRect(self, *args, **kwargs):
        return QRectF(0, 0, self.w, self.h)

    # def hoverEnterEvent(self, *args, **kwargs):
    #     QGraphicsItem.hoverEnterEvent(self, *args, **kwargs)
    #     self.update(self.boundingRect())
    #
    #
    # def hoverLeaveEvent(self, *args, **kwargs):
    #     QGraphicsItem.hoverLeaveEvent(self, *args, **kwargs)
    #     self.update(self.boundingRect())

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        # c = hoverColor if self.isUnderMouse() else selColor
        # qPainter.setPen(QPen(hoverColor, 3, Qt.SolidLine))
        # qPainter.drawLine(-self.w/2, 0, self.w/2, 0)
        # qPainter.drawLine(0, -self.h/2, 0, self.h/2)
        style = self.getStyle()
        if style.background_color:
            qPainter.fillRect(self.boundingRect(), style.background_color)

    def dragMove(self, delta, suggestedPosition):
        self.on_drag(delta, suggestedPosition)