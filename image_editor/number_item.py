from pyqode.qt.QtCore import Qt, QRectF, QPointF
from pyqode.qt.QtWidgets import QGraphicsItem, QPen, QColor, QPainter, QPainterPath

from item_style import ItemStyles
from item_base import ItemBase
from enums import RectAnchors


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
        self.size = 30
        self.fontSize = 14
        self.margin = 0
        self.constr = constr
        self.startPoint = QPointF()

    def setNunber(self, n):
        self.number = n
        self.update()

    def dragStart(self, startPoint):
        self.startPoint = self.pos()

    def dragMove(self, delta, totalDelta):
        self.setPos(self.constr(self.startPoint + totalDelta))

    def boundingRect(self, *args, **kwargs):
        s = self.size + 2 * self.margin
        x = - self.margin - self.size / 2
        y = - self.margin - self.size / 2
        return QRectF(x, y, s, s)

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):

        style = self.getStyle()

        qPainter.save()

        if style.antialiased:
            qPainter.setRenderHint(QPainter.Antialiasing, True)

        qPainter.setRenderHint(QPainter.TextAntialiasing, True)

        # f = qPainter.font()
        from pyqode.qt.QtWidgets import QFont
        f = QFont('Open Sans', self.fontSize)
        f.setPointSize(self.fontSize)
        qPainter.setFont(f)

        x = -self.size / 2 - self.margin
        y = -self.size / 2 - self.margin
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

        qPainter.restore()

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

    def __init__(self, numberProvider, constr, on_corner_change, sizeProvider, corner=RectAnchors.LeftTop, style=None):
        NumberItem.__init__(self, numberProvider, constr, style)
        self.corner = corner
        self._change_trigger_ = on_corner_change
        self.scaleFactor = 1.0
        self.sizeProvider = sizeProvider
        self.dragCount = QPointF()

    def setSizeScale(self, scale):
        self.scaleFactor = 1.0 * scale

    def dragStart(self, startPoint):
        print 'clearing drag value'
        self.dragCount = QPointF()

    def dragMove(self, delta, totalDelta):
        d = delta

        if self.dragCount.x() == self.dragCount.y():
            horizontal = abs(d.x()) > abs(d.y())
        else:
            horizontal = abs(self.dragCount.x()) > abs(self.dragCount.y())

        self.dragCount = self.dragCount + d
        drag = self.dragCount.x() if horizontal else self.dragCount.y()
        corner = None

        # treshhold = AnchoredNumberItem.dragStrength * self.scaleFactor #abs(totalDelta.x()) if horizontal else abs(totalDelta.y()) #
        # treshhold = treshhold * AnchoredNumberItem.dragStrength

        treshold = self.sizeProvider().width()/2 if horizontal else self.sizeProvider().height()/2
        # print drag, treshold

        if horizontal and drag > treshold:
            corner = RectAnchors.toRight(self.corner)
            self.dragCount = QPointF()
        elif horizontal and drag < -treshold:
            corner = RectAnchors.toLeft(self.corner)
            self.dragCount = QPointF()
        elif not horizontal and drag > treshold:
            corner = RectAnchors.toBottom(self.corner)
            self.dragCount = QPointF()
        elif not horizontal and drag < -treshold:
            corner = RectAnchors.toUp(self.corner)
            self.dragCount = QPointF()

        if corner is not None:
            self.corner = corner
            # print "Corner changed", corner
            self._change_trigger_()

    # def setSelected(self, *args, **kwargs):
    #     NumberItem.setSelected()
