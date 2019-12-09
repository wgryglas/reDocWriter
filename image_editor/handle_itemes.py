
from pyqode.qt.QtCore import Qt, QSizeF, QRectF, QPointF, Signal

from pyqode.qt.QtWidgets import QGraphicsItem, QPen, QColor, QPainter, QPainterPath, QGraphicsRectItem, \
    QGraphicsPixmapItem, QPixmap, QTransform

from item_style import ItemStyles, GraphicsStyle
from item_base import ItemBase

# from pyqode.qt.QtWidgets import QGraphicsDropShadowEffect
# effect = QGraphicsDropShadowEffect()
# effect.setEnabled(False)
# self.image.setGraphicsEffect(effect)

def makeArrowStyle():
    styles = ItemStyles(background_color=QColor(100, 136, 255, 100))
    styles.set_style('hover', border_color=ItemStyles.hoverColor)
    styles.set_style('select', background_color=QColor(100, 136, 255, 100))
    return styles


class ExtensionArrow(ItemBase):
    def __init__(self, orientation, initial_provider, on_drag, style=makeArrowStyle()):
        ItemBase.__init__(self, style)
        self.image = QGraphicsPixmapItem(QPixmap('/home/wgryglas/Code/Python/reDocsEditor/assets/icons/arrow-down.png'))
        self.image.setParentItem(self)
        self.on_drag = on_drag
        self._rect_ = QRectF(0, 0, 0, 0)
        self.sizeScale = 1.0
        self.orientation = orientation
        self.initProvider = initial_provider

        self.posTransform = QTransform()
        self.translationTransform = QTransform()
        self.orientationTransform = QTransform()
        self.scaleTransform = QTransform()

        ir = self.image.boundingRect()
        self.imageSize = QSizeF(ir.width(), ir.height())
        self.image.setTransform(QTransform.fromTranslate(-self.imageSize.width() / 2, -self.imageSize.height() / 2))

        self.base_rect = QRectF(-15, -7.5, 30, 15)

        self.startValue = 0.0

        if orientation == 'up':
            self.orientationTransform.rotate(180)
            self.translationTransform.translate(0, -7.5)
        elif orientation == 'right':
            self.orientationTransform.rotate(-90)
            self.translationTransform.translate(7.5, 0)
        elif orientation == 'left':
            self.orientationTransform.rotate(90)
            self.translationTransform.translate(-7.5, 0)
        else:
            self.translationTransform.translate(0, 7.5)

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setAcceptHoverEvents(True)

        self.updateTransforms()

    def updateTransforms(self):
        total = self.scaleTransform * self.orientationTransform * self.translationTransform * self.posTransform
        self.setTransform(total)

    def setPos(self, x, y):
        self.posTransform.reset()
        self.posTransform.translate(x, y)
        self.updateTransforms()

    # def rect(self):
    #     tr = self.posTransform * self.translationTransform * self.orientationTransform
    #     return tr.mapRect(self.base_rect)

    # def viewRect(self):
    #     return self.transform().mapRect(self.base_rect)

    def boundingRect(self, *args, **kwargs):
        return self.base_rect

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        style = self.getStyle()

        r = self.base_rect #self.viewRect()

        if style.background_color:
            qPainter.setPen(style.background_color)
            qPainter.fillRect(r, style.background_color)

        if style.border_color:
            qPainter.setPen(style.border_color)
            qPainter.drawRect(r)

    def isConstantSize(self):
        return True

    def setSizeScale(self, scale):
        self.scaleTransform.reset()
        self.scaleTransform.scale(scale, scale)
        self.updateTransforms()

    def dragStart(self, startPoint):
        self.startValue = self.initProvider()

    def dragMove(self, delta, total):
        if self.orientation == 'up':
            self.on_drag(self.startValue - total.y())
        elif self.orientation == 'down':
            self.on_drag(self.startValue + total.y())
        elif self.orientation == 'left':
            self.on_drag(self.startValue - total.x())
        else:
            self.on_drag(self.startValue + total.x())


def makeHandleStyle():
    styles = ItemStyles(background_color=ItemStyles.markColor)
    styles.set_style('hover', background_color=ItemStyles.hoverColor)
    styles.set_style('select', background_color=ItemStyles.markColor)
    return styles


class MoveHandle(ItemBase):

    def __init__(self, initialPointProvider, on_drag, w=12, h=12, style=None):
        ItemBase.__init__(self, style if style else makeHandleStyle())
        self.w = w
        self.h = h
        self.initProvider = initialPointProvider
        self.on_drag = on_drag
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        # self.setFlag(QGraphicsItem.ITem)
        self.setAcceptHoverEvents(True)
        self.startPoint = QPointF()

        self.translation = QTransform()
        self.scale = QTransform()

    def boundingRect(self, *args, **kwargs):
        return QRectF(-self.w/2, -self.h/2, self.w, self.h)

    def updateTransform(self):
        self.setTransform(self.scale * self.translation)

    def setPos(self, x, y):
        self.translation.reset()
        self.translation.translate(x, y)
        self.updateTransform()

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        style = self.getStyle()
        if style.background_color:
            qPainter.fillRect(self.boundingRect(), style.background_color)

    def setSizeScale(self, scale):
        self.scale.reset()
        self.scale.scale(scale, scale)
        self.updateTransform()

    def isConstantSize(self):
        return True

    def dragStart(self, startPoint):
        self.startPoint = self.initProvider()

    def dragMove(self, delta, total):
        self.on_drag(self.startPoint + total)
