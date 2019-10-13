

from pyqode.qt.QtCore import Qt, QSizeF, QRectF, QPointF, Signal
from pyqode.qt.QtWidgets import QGraphicsView, QGraphicsItem, QPen, QColor, QPainter, QGraphicsScene, QPixmap, \
    QGraphicsLineItem, QPainterPath, QGraphicsRectItem, QGraphicsPixmapItem, QMainWindow, QWidget, QPushButton, \
    QCheckBox, QSpinBox, QLineEdit, QHBoxLayout, QVBoxLayout, QStyle


markColor = QColor(100, 136, 255)
selColor = QColor(80, 110, 200)


class NumberItem(QGraphicsItem):
    def __init__(self, numberProvider, constr):
        QGraphicsItem.__init__(self)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.number = numberProvider.nextNumber()
        self.numberProvider = numberProvider
        self.size = 40
        self.margin = 0
        self.constr = constr

    def dragMove(self, delta):
        self.setPos(self.constr(self.pos() + delta))

    def boundingRect(self, *args, **kwargs):
        s = self.size + 2 * self.margin
        x = - self.margin
        y = - self.margin
        return QRectF(x, y, s, s)

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        qPainter.setRenderHint(QPainter.Antialiasing, True)
        qPainter.setRenderHint(QPainter.TextAntialiasing, True)

        f = qPainter.font()
        f.setPointSize(16)
        qPainter.setFont(f)

        x = 0
        y = 0
        path = QPainterPath()
        path.addRoundedRect(x, y, self.size, self.size, self.size, self.size)
        qPainter.fillPath(path, selColor if self.isSelected() else markColor)

        qPainter.setPen(QColor(255, 255, 255))
        qPainter.drawText(QRectF(x, y, self.size, self.size), Qt.AlignCenter, str(self.number))

        if self.isSelected():
            qPainter.setPen(QPen(QColor(100, 100, 100, 100), 1, Qt.DashLine))
            s = self.size
            qPainter.drawRect(x, y, s, s)

    def clone(self):
        item = NumberItem(self.numberProvider, self.constr)
        p = self.pos()
        s = self.constr.spacing
        item.setPos(p.x()+5*s, p.y()+5*s)
        return item


class ExtensionArrow(QGraphicsPixmapItem):

    def __init__(self, orientation, on_drag):
        QGraphicsPixmapItem.__init__(self, QPixmap('/home/wgryglas/Code/Python/reDocsEditor/assets/icons/arrow-down.png'))

        self.on_drag = on_drag

        if orientation == 'up':
            self.rotate(180)
        elif orientation == 'left':
            self.rotate(90)
        elif orientation == 'right':
            self.rotate(-90)

        self.orientation = orientation

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        qPainter.fillRect(2, 2, 12, 12, QColor(100, 136, 255, 100))
        QGraphicsPixmapItem.paint(self, qPainter, qStyleOptionGraphicsItem, qWidget)

    def dragMove(self, delta):
        self.on_drag(delta.y())


class RectSelectionItem(QGraphicsItem):
    def __init__(self, size, constr):
        QGraphicsItem.__init__(self)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.size = size
        self.lineWidth = 3
        self.color = markColor
        self.padding = 16
        self.constr = constr

        down = ExtensionArrow('down', lambda v: self.setRect(self.x, self.y, self.width, self.height+v))
        down.setParentItem(self)

        up = ExtensionArrow('up', lambda v: self.setRect(self.x, self.y-v, self.width, self.height+v))
        up.setParentItem(self)

        left = ExtensionArrow('left', lambda v: self.setRect(self.x-v, self.y, self.width+v, self.height))
        left.setParentItem(self)

        right = ExtensionArrow('right', lambda v: self.setRect(self.x, self.y, self.width+v, self.height))
        right.setParentItem(self)

        self.arrows = [left, right, up, down]
        self.setRect(0, 0, size.width(), size.height())

        for a in self.arrows:
            a.setVisible(False)

    def dragUp(self, v):
        p = self.pos()
        self.setPos(p.x(), p.y() - v)
        self.setSize(self.width, self.height + v)

    def dragLeft(self, v):
        p = self.pos()
        self.setSize(self.width+v, self.height)
        self.setPos(p.x() - v, p.y())
        self.setRect()

    def dragRight(self, v):
        self.setSize(self.width+v, self.height)

    def setRect(self, x, y, w, h):
        # if self.x == x and self.y == y and self.width == w and self.height == h:
        #     return
        if w <= 0:
            w = self.width

        if h <= 0:
            h = self.height

        self.arrows[0].setPos(0, h/2-8)
        self.arrows[1].setPos(w, h/2+8)

        self.arrows[2].setPos(w/2+8, 0)
        self.arrows[3].setPos(w/2-8, h)

        min = self.constr(QPointF(x, y))
        max = self.constr(QPointF(x+w,y+h))

        self.size = QSizeF(max.x()-min.x(), max.y()-min.y())

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
        return QRectF(-self.padding, -self.padding, self.size.width()+2*self.padding, self.size.height()+2*self.padding)

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):

        sel = self.isSelected()
        if not sel:
            sel = any([a.isSelected() for a in self.arrows])

        need_redraw = False
        for a in self.arrows:
            if not sel and a.isVisible():
                need_redraw = True
            a.setVisible(sel)

        qPainter.setPen(QPen(selColor if sel else markColor, self.lineWidth, Qt.SolidLine))
        qPainter.drawRect(0, 0, self.width, self.height)

        #force redraw on child selection changed
        if need_redraw:
            p = self.pos()
            self.setPos(p.x()-1, p.y()-1)
            self.setPos(p.x(), p.y())

        # if self.isSelected():
        #     path = QPainterPath()
        #     path.addEllipse(self.width-self.padding, self.height-self.padding, 2*self.padding, 2*self.padding)
        #     qPainter.fillPath(path, QColor(236, 208, 137))

    def dragMove(self, delta):
        self.setPos(self.constr(self.pos() + delta))

    def clone(self):
        item = RectSelectionItem(self.size, self.constr)
        p = self.pos()
        s = self.constr.spacing
        item.setPos(p.x()+5*s, p.y()+5*s)
        return item


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


class ImageScene(QGraphicsScene):

    def __init__(self, imageUrl=None):
        QGraphicsScene.__init__(self)
        self.imgItem = None
        self.gridLines = []
        self.spacing = 10

        self.posConstr = PosConstraint(self.spacing)

        self.pressPos = None
        self.draggingItems = dict()
        self.recentPos = QPointF()

        if imageUrl:
            self.setImage(imageUrl)

        self.userItems = []

    def selectedElements(self):
        return [item for item in self.selectedItems() if item.parentItem() == self.imgItem]

    def setSpacing(self, spacing):
        self.spacing = spacing
        self.updateGrid()

    def setImage(self, url):
        if self.imgItem:
            self.removeItem(self.imgItem)
            del self.imgItem
        pxm = QPixmap(url)
        self.imgItem = self.addPixmap(pxm)
        self.updateGrid()

    def updateGrid(self):
        rect = self.imgItem.boundingRect()
        w = rect.width()
        h = rect.height()

        for i in self.gridLines:
            self.imgItem.removeItem(i)
            del i
        self.gridLines = []

        if self.spacing == 1:
            return

        color = QColor(100, 100, 100, 20)

        x = 0
        while x <= w:
            item = QGraphicsLineItem(x, 0, x, h)
            item.setPen(color)
            item.setParentItem(self.imgItem)
            self.gridLines.append(item)
            x += self.spacing

        y = 0
        while y <= h:
            item = QGraphicsLineItem(0, y, w, y)
            item.setParentItem(self.imgItem)
            item.setPen(color)
            self.gridLines.append(item)
            y += self.spacing

    def addNumberElement(self, numberProvider):
        if not self.imgItem:
            raise ValueError('Image must be set before adding elements')
        item = NumberItem(numberProvider, self.posConstr)
        item.setParentItem(self.imgItem)
        item.setPos(self.recentPos)
        self.userItems.append(item)
        return item

    def addRectElement(self):
        if not self.imgItem:
            raise ValueError('Image must be set before adding elements')

        item = RectSelectionItem(QSizeF(100, 50), self.posConstr)
        item.setPos(self.recentPos)
        item.setParentItem(self.imgItem)
        self.userItems.append(item)

        return item

    def duplicateSelection(self):
        newEl = [e.clone() for e in self.selectedElements()]
        self.clearSelection()
        for e in newEl:
            e.setParentItem(self.imgItem)
            e.setSelected(True)
            self.userItems.append(e)

    def mousePressEvent(self, e):
        QGraphicsScene.mousePressEvent(self, e)
        self.recentPos = e.pos()
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
            p = e.pos()
            delta = QPointF(p.x() - self.pressPos.x(), p.y() - self.pressPos.y())
            delta = self.posConstr(delta)

            #drag multiple only on root items, otherwise extra handles would be triggered
            items = self.draggingItems.keys()
            if len(self.draggingItems) > 1:
                items = filter(lambda i: i.parentItem() == self.imgItem, self.draggingItems.keys())

            for item in items:
                item.dragMove(delta)

    def renderToFile(self, path):
        from pyqode.qt.QtGui import QImage

        for line in self.gridLines:
            line.setVisible(False)

        self.clearSelection()
        self.setSceneRect(self.itemsBoundingRect())

        image = QImage(self.sceneRect().size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        self.render(painter)
        painter.end()

        image.save(path)

        for line in self.gridLines:
            line.setVisible(True)

    def deleteSelected(self):
        for e in self.selectedElements():
            self.removeItem(e)
            del e


class ImageCanvas(QGraphicsView):

    def __init__(self, *args):
        QGraphicsView.__init__(self, *args)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def saveWidgetAs(self, path):
        self.scene().deselectAll()
        QPixmap.grabWidget(self).save(path)


class EditImageWindow(QMainWindow):

    on_saved = Signal()
    on_exit = Signal()

    def __init__(self, path):
        QMainWindow.__init__(self)
        self.path = path
        self.scene = ImageScene(imageUrl=path)
        self.view = ImageCanvas(self.scene)

        self.numberIter = 1

        self.enabledOnSelection = []

        self.do_layout()

        self.scene.selectionChanged.connect(self.update_enabled)

    def nextNumber(self):
        v = self.numberIter
        self.numberIter += 1
        return v

    def update_enabled(self):
        sel = len(self.scene.selectedElements()) > 0
        for button in self.enabledOnSelection:
            button.setEnabled(sel)

    def layout_buttons(self):
        import icons

        panel = QWidget()
        panel.setObjectName('buttons-bar')

        add_rect = QPushButton()
        add_rect.setIcon(icons.get('rectangle'))
        add_rect.setToolTip('Add Rectangle')
        add_rect.clicked.connect(self.scene.addRectElement)

        add_number = QPushButton()
        add_number.setToolTip('Add number')
        add_number.setIcon(icons.get('add_number'))
        add_number.clicked.connect(lambda: self.scene.addNumberElement(self))

        duplicate_button = QPushButton()
        duplicate_button.setToolTip('Duplicate')
        duplicate_button.setIcon(icons.get('duplicate'))
        duplicate_button.setEnabled(False)
        duplicate_button.clicked.connect(lambda: self.scene.duplicateSelection())
        self.enabledOnSelection.append(duplicate_button)


        delete_button = QPushButton()
        delete_button.setToolTip('Delete')
        delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_button.setEnabled(False)
        delete_button.clicked.connect(lambda: self.scene.deleteSelected())
        self.enabledOnSelection.append(delete_button)

        lt = QHBoxLayout()
        lt.addWidget(add_rect)
        lt.addWidget(add_number)
        lt.addSpacing(20)
        lt.addWidget(duplicate_button)
        lt.addSpacing(20)
        lt.addWidget(delete_button)
        lt.addStretch()
        panel.setLayout(lt)

        return panel

    def do_layout(self):
        panel = QWidget()
        bar = self.layout_buttons()
        lt = QVBoxLayout()
        lt.addWidget(bar)
        lt.addWidget(self.view)
        panel.setLayout(lt)

        self.setCentralWidget(panel)

    def closeEvent(self, event):
        if len(self.scene.userItems) > 0:
            from pyqode.qt.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, 'Save changes',
                                               "Do you want to save changes?", QMessageBox.Yes, QMessageBox.No) #QMessageBox.Cancel,
            if reply == QMessageBox.Yes:
                self.scene.renderToFile(self.path)
                self.on_saved.emit()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
            self.on_exit.emit()
            event.accept()


def main():
    from pyqode.qt.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    win = EditImageWindow("/home/wgryglas/test-im-edit.png.png")
    win.show()


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()