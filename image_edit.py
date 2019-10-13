

from pyqode.qt.QtCore import Qt, QSize, QRectF, QPointF
from pyqode.qt.QtWidgets import QGraphicsView, QGraphicsItem, QPen, QColor, QPainter, QGraphicsScene, QPixmap, \
    QGraphicsLineItem, QPainterPath, QFontMetrics, QGraphicsEllipseItem, QGraphicsTextItem


markColor = QColor(100, 136, 255)


class NumberItem(QGraphicsItem):
    def __init__(self, number):
        QGraphicsItem.__init__(self)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.number = number
        self.size = 50

    def boundingRect(self, *args, **kwargs):
        p = self.pos()
        return QRectF(p.x(), p.y(), self.size, self.size)

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        qPainter.setRenderHint(QPainter.Antialiasing, True)
        qPainter.setRenderHint(QPainter.TextAntialiasing, True)
        f = qPainter.font()
        f.setPointSize(16)
        qPainter.setFont(f)
        fm = QFontMetrics(f)
        text = str(self.number)
        fW = fm.width(text)
        fH = fm.xHeight()+2

        pos = self.pos()
        # qPainter.fillRoundRect(pos.x(), pos.y(), self.size, self.size, self.size, self.size)
        path = QPainterPath()
        path.addRoundedRect(pos.x(), pos.y(), self.size, self.size, self.size, self.size)
        qPainter.fillPath(path, markColor)

        qPainter.setPen(QColor(255, 255, 255))
        qPainter.drawText(QRectF(pos.x()+self.size/2-fW/2, pos.y()+self.size/2-fH, self.size-10, self.size-10), str(self.number))


class PosConstraint:
    def __init__(self, spacing):
        self.spacing = spacing

    def __call__(self, pnt):
        if self.spacing == 1:
            return pnt

        ix = int(pnt.x())
        iy = int(pnt.y())
        x = (ix / self.spacing) * self.spacing
        # if ix % self.spacing >= 5:
        #     x += self.spacing
        y = (iy / self.spacing) * self.spacing
        # if iy % self.spacing >= 5:
        #     y += self.spacing

        return QPointF(x, y)


class NumberItem2(QGraphicsEllipseItem):
    def __init__(self, number, posConstr, x=0, y=0, size=40):
        QGraphicsEllipseItem.__init__(self, x, y, size, size)

        self.number = number
        self.constr = posConstr

        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)

        self.setBrush(markColor)
        self.setPen(markColor)

        numStr = str(number)
        self.text = QGraphicsTextItem(numStr)
        self.text.setParentItem(self)
        self.text.setDefaultTextColor(QColor(255, 255, 255))
        self.text.setTextWidth(size)
        f = self.text.font()
        f.setPointSize(16)
        fm = QFontMetrics(f)
        fW = fm.width(numStr)
        self.text.setPos(size/2-fW/2-4, 3)
        self.text.setFont(f)

        self.startPos = None
        self.startDragPoint = None

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        qPainter.setRenderHint(QPainter.Antialiasing, True)
        qPainter.setRenderHint(QPainter.TextAntialiasing, True)
        QGraphicsEllipseItem.paint(self, qPainter, qStyleOptionGraphicsItem, qWidget)


class ImageScene(QGraphicsScene):

    def __init__(self, imageUrl=None):
        QGraphicsScene.__init__(self)
        self.imgItem = None
        self.gridLines = []
        self.spacing = 20

        self.posConstr = PosConstraint(self.spacing)

        self.pressPos = None
        self.draggingItems = dict()

        if imageUrl:
            self.setImage(imageUrl)


    def setImage(self, url):
        if self.imgItem:
            self.removeItem(self.imgItem)
            del self.imgItem
        pxm = QPixmap(url)
        self.imgItem = self.addPixmap(pxm)
        self.setGrid()

    def setGrid(self):
        rect = self.imgItem.boundingRect()
        w = rect.width()
        h = rect.height()

        for i in self.gridLines:
            self.removeItem(i)
            del i
        self.gridLines = []

        color = QColor(100, 100, 100, 20)

        x = 0
        while x <= w:
            item = QGraphicsLineItem(x, 0, x, h)
            item.setPen(color)
            item.setParentItem(self.imgItem)
            x += self.spacing

        y = 0
        while y <= h:
            item = QGraphicsLineItem(0, y, w, y)
            item.setParentItem(self.imgItem)
            item.setPen(color)
            y += self.spacing

    def addNumberItem(self, number):
        if not self.imgItem:
            raise ValueError('Image must be set before adding elements')
        item = NumberItem2(number, self.posConstr)
        item.setParentItem(self.imgItem)
        return item

    def mousePressEvent(self, e):
        QGraphicsScene.mousePressEvent(self, e)

        self.draggingItems = dict()

        if len(self.selectedItems()):
            self.pressPos = e.pos()
            for item in self.selectedItems():
                self.draggingItems[item] = item.pos()


    def mouseReleaseEvent(self, e):
        QGraphicsScene.mouseReleaseEvent(self, e)
        self.pressPos = None

    def mouseMoveEvent(self, e):
        QGraphicsScene.mouseMoveEvent(self, e)
        if self.pressPos:
            print 'move'
            p = e.pos()
            delta = QPointF(p.x() - self.pressPos.x(), p.y() - self.pressPos.y())
            delta = self.posConstr(delta)
            for item in self.draggingItems:
                op = item.pos()
                np = QPointF(op.x()+delta.x(), op.y()+delta.y())
                item.setPos(np)



class ImageCanvas(QGraphicsView):

    def __init__(self, *args):
        QGraphicsView.__init__(self, *args)
    # def paintEvent(self, *args, **kwargs):
    #     QGraphicsView.paintEvent(self, *args, **kwargs)


def main():
    from pyqode.qt.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    sc = ImageScene("/home/wgryglas/Code/Python/pelicanReDoc/content/figures/test/drawing.png")

    sc.addNumberItem(5).setPos(QPointF(100, 0))
    sc.addNumberItem(10).setPos(QPointF(200, 0))

    ex = ImageCanvas(sc)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()