from pyqode.qt.QtCore import Qt, QRectF
from pyqode.qt.QtWidgets import QGraphicsItem, QPen, QColor, QPainter, QPainterPath

from item_style import ItemStyles
from item_base import ItemBase
from rect_postion import CornerPosition


def makeStyle():
    styles = ItemStyles(background_color=ItemStyles.markColor, antialiased=True)
    styles.set_style('select', background_color=ItemStyles.selColor)
    styles.set_style('hover', background_color=ItemStyles.hoverColor)
    return styles


class NumberItem(ItemBase):

    def __init__(self, numberProvider, constr, style=None):
        ItemBase.__init__(self, style if style else makeStyle())
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.number = numberProvider.nextNumber()
        self.numberProvider = numberProvider
        self.size = 40
        self.margin = 0
        self.constr = constr

    def setNunber(self, n):
        self.number = n
        self.update()

    def dragMove(self, delta, suggestedPosition):
        self.setPos(self.constr(self.pos() + delta))

    def boundingRect(self, *args, **kwargs):
        s = self.size + 2 * self.margin
        x = - self.margin
        y = - self.margin
        return QRectF(x, y, s, s)

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):

        style = self.getStyle()

        if style.antialiased:
            qPainter.setRenderHint(QPainter.Antialiasing, True)

        qPainter.setRenderHint(QPainter.TextAntialiasing, True)

        f = qPainter.font()
        f.setPointSize(16)
        qPainter.setFont(f)

        x = 0
        y = 0
        path = QPainterPath()
        path.addRoundedRect(x, y, self.size, self.size, self.size, self.size)

        if style.background_color:
            qPainter.setPen(style.background_color)
            qPainter.fillPath(path, style.background_color)

        if style.border_color:
            qPainter.setPen(style.border_color)
            qPainter.drawPath(path)

        if style.foreground_color:
            qPainter.setPen(style.foreground_color)
            qPainter.drawText(QRectF(x, y, self.size, self.size), Qt.AlignCenter, str(self.number))

        if self.isSelected():
            qPainter.setPen(QPen(QColor(100, 100, 100, 100), 1, Qt.DashLine))
            s = self.size
            qPainter.drawRect(x, y, s, s)

    def clone(self):
        item = NumberItem(self.numberProvider, self.constr, self.styles)
        p = self.pos()
        s = self.constr.spacing
        item.setPos(p.x()+5*s, p.y()+5*s)
        return item

    def properties(self):
        from properties import IntProperty
        return [IntProperty('Number', lambda v: self.setNunber(v), lambda: self.number)]


class AnchoredNumberItem(NumberItem):

    dragStrength = 3

    def __init__(self, numberProvider, constr, on_position_change, corner=CornerPosition.top_left, style=None):
        NumberItem.__init__(self, numberProvider, constr, style)
        self.corner = corner
        self._change_trigger_ = on_position_change
        self.scaleFactor = 1.0

    def setSizeScale(self, scale):
        self.scaleFactor = 1.0 * scale

    def dragMove(self, delta, suggestedPosition):

        horizontal = abs(delta.x()) > abs(delta.y())

        corner = None

        treshhold = AnchoredNumberItem.dragStrength * self.scaleFactor

        if horizontal and delta.x() > treshhold:
            corner = self.corner.toRight
        elif horizontal and delta.x() < -treshhold:
            corner = self.corner.toLeft
        elif not horizontal and delta.y() > treshhold:
            corner = self.corner.toDown
        elif not horizontal and delta.y() < -treshhold:
            corner = self.corner.toUp

        if corner is not None:
            self.corner = corner
            self._change_trigger_()

    # def setSelected(self, *args, **kwargs):
    #     NumberItem.setSelected()
