from pyqode.qt.QtCore import Qt, QSizeF, QRectF, QPointF, Signal
from pyqode.qt.QtWidgets import QGraphicsView, QGraphicsItem, QPen, QColor, QPainter, QGraphicsScene, QPixmap, \
    QGraphicsLineItem, QPainterPath, QGraphicsRectItem, QGraphicsPixmapItem, QMainWindow, QWidget, QPushButton, \
    QCheckBox, QSpinBox, QLineEdit, QHBoxLayout, QVBoxLayout, QStyle, QIntValidator, QLabel

markColor = QColor(100, 136, 255)
selColor = QColor(80, 110, 200)
hoverColor = QColor(255, 0, 0)

class Corner:
    def __init__(self, toLeft, toRight, toDown, toUp):
        self.toLeft = toLeft
        self.toRight = toRight
        self.toUp = toUp
        self.toDown = toDown


class CornerPosition:
    top_left = Corner(None, None, None, None)
    top_right = Corner(None, None, None, None)
    bottom_right = Corner(None, None, None, None)
    bottom_left = Corner(None, None, None, None)


CornerPosition.top_left.toRight = CornerPosition.top_right
CornerPosition.top_left.toDown = CornerPosition.bottom_left

CornerPosition.top_right.toLeft = CornerPosition.top_left
CornerPosition.top_right.toDown = CornerPosition.bottom_right

CornerPosition.bottom_left.toRight = CornerPosition.bottom_right
CornerPosition.bottom_left.toUp = CornerPosition.top_left

CornerPosition.bottom_right.toLeft = CornerPosition.bottom_left
CornerPosition.bottom_right.toUp = CornerPosition.top_right


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


class ExtensionArrow(QGraphicsRectItem):

    def __init__(self, orientation, on_drag):
        QGraphicsRectItem.__init__(self)

        image = QGraphicsPixmapItem(QPixmap('/home/wgryglas/Code/Python/reDocsEditor/assets/icons/arrow-down.png'))
        image.setParentItem(self)
        self.on_drag = on_drag

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

        self.setBrush(QColor(100, 136, 255, 100))
        self.setPen(QColor(100, 136, 255, 100))

        self.orientation = orientation

        image.setFlag(QGraphicsItem.ItemIsSelectable, False)

        self.image = image

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setAcceptHoverEvents(True)

        # self.setFlag(QGraphicsItem.ItemIsFocusable)

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        # qPainter.fillRect(2, 2, 28, 18, QColor(100, 136, 255, 100))

        if self.isUnderMouse() or self.image.isUnderMouse():
            self.setBrush(hoverColor)
        else:
            self.setBrush(QColor(100, 136, 255, 100))

        QGraphicsRectItem.paint(self, qPainter, qStyleOptionGraphicsItem, qWidget)

    def dragMove(self, delta):
        if self.orientation == 'up':
            self.on_drag(-delta.y())
        elif self.orientation == 'down':
            self.on_drag(delta.y())
        elif self.orientation == 'left':
            self.on_drag(-delta.x())
        else:
            self.on_drag(delta.x())


class MoveHandle(QGraphicsItem):

    def __init__(self, on_drag, w=12, h=12):
        QGraphicsItem.__init__(self)
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
        c = hoverColor if self.isUnderMouse() else selColor
        # qPainter.setPen(QPen(hoverColor, 3, Qt.SolidLine))
        # qPainter.drawLine(-self.w/2, 0, self.w/2, 0)
        # qPainter.drawLine(0, -self.h/2, 0, self.h/2)

        qPainter.fillRect(self.boundingRect(), c)

    def dragMove(self, delta):
        self.on_drag(delta)


class RectSelectionItem(QGraphicsItem):
    def __init__(self, size, constr):
        QGraphicsItem.__init__(self)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.size = size
        self.lineWidth = 3
        self.color = markColor
        self.padding = 16
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

        self.posHandle = MoveHandle(lambda d: self.setPos(self.constr(self.pos() + d)))
        self.posHandle.setParentItem(self)

        self.arrows = [left, right, up, down]
        self.setRect(0, 0, size.width(), size.height())

        self.activeItems = [self.posHandle]
        self.activeItems.extend(self.arrows)

        for a in self.activeItems:
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

        self.arrows[0].setPos(0, (h-self.arrows[0].rect().height())/2 )
        self.arrows[1].setPos(w, (h-self.arrows[1].rect().height())/2 )

        self.arrows[2].setPos((w-self.arrows[2].rect().width())/2, 0)
        self.arrows[3].setPos((w-self.arrows[3].rect().width())/2, h)

        min = self.constr(QPointF(x, y))
        max = self.constr(QPointF(x+w,y+h))

        self.size = QSizeF(max.x()-min.x(), max.y()-min.y())

        self.posHandle.setPos(-self.posHandle.w / 2 + self.size.width()/2, -self.posHandle.h / 2 + self.size.height()/2)

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

    def paintItem(self, qPainter, selected):
        qPainter.setRenderHints(QPainter.Antialiasing, False)
        qPainter.setRenderHints(QPainter.HighQualityAntialiasing, False)
        qPainter.setPen(QPen(selColor if selected else markColor, self.lineWidth, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        qPainter.drawRect(0, 0, self.width, self.height)

    def paint(self, qPainter, qStyleOptionGraphicsItem, qWidget):
        qPainter.setRenderHint(QPainter.Antialiasing, True)
        qPainter.setRenderHint(QPainter.TextAntialiasing, True)

        sel = self.isSelected()
        if not sel:
            sel = any([a.isSelected() for a in self.activeItems])

        need_redraw = False
        for a in self.activeItems:
            if not sel and a.isVisible():
                need_redraw = True
            a.setVisible(sel)

        self.paintItem(qPainter, sel)

        #force redraw on child selection changed
        if need_redraw:
            # self.update(self.boundingRect())
            p = self.pos()
            self.setPos(p.x()-1, p.y()-1)
            self.setPos(p.x(), p.y())

    def dragMove(self, delta):
        pass
        # self.setPos(self.constr(self.pos() + delta))

    def clone(self):
        item = RectSelectionItem(self.size, self.constr)
        p = self.pos()
        s = self.constr.spacing
        item.setPos(p.x()+5*s, p.y()+5*s)
        return item


class EllipseSelectionItem(RectSelectionItem):
        def __init__(self, size, constr):
            RectSelectionItem.__init__(self, size, constr)

        def paintItem(self, qPainter, selected):
            qPainter.setPen(QPen(selColor if selected else markColor, self.lineWidth, Qt.SolidLine))
            qPainter.drawEllipse(0, 0, self.width, self.height)

        def clone(self):
            return EllipseSelectionItem(self.size, self.constr)


class AnchoredNumberItem(NumberItem):

    dragStrength = 50

    def __init__(self, numberProvider, constr, on_position_change, corner=CornerPosition.top_left):
        NumberItem.__init__(self, numberProvider, constr)
        self.corner = corner
        self._change_trigger_ = on_position_change

    def dragMove(self, delta):
        horizontal = abs(delta.x()) > abs(delta.y())

        corner = None

        if horizontal and delta.x() > AnchoredNumberItem.dragStrength:
            corner = self.corner.toRight
        elif horizontal and delta.x() < -AnchoredNumberItem.dragStrength:
            corner = self.corner.toLeft
        elif not horizontal and delta.y() > AnchoredNumberItem.dragStrength:
            corner = self.corner.toDown
        elif not horizontal and delta.y() < -AnchoredNumberItem.dragStrength:
            corner = self.corner.toUp

        if corner is not None:
            self.corner = corner
            self._change_trigger_()

    # def setSelected(self, *args, **kwargs):
    #     NumberItem.setSelected()


class RectNumberedItem(RectSelectionItem):
    def __init__(self, size, constr, numberProvider):
        RectSelectionItem.__init__(self, size, constr)
        self.number = AnchoredNumberItem(numberProvider, constr, self.positionNumber)
        self.number.setParentItem(self)
        self.activeShift = 0
        self.numberShift = -5

        self.positionNumber()

    def paintItem(self, qPainter, selected):
        self.activeNumber(selected)
        RectSelectionItem.paintItem(self, qPainter, selected)

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

    def activeNumber(self, apart):
        self.activeShift = 0 if not apart else self.number.size / 2
        self.positionNumber()

        # #force redraw
        # self.setPos(self.x-1, self.y-1)
        # self.setPos(self.x+1, self.y+1)
        self.scene().update()


    def clone(self):
        return RectNumberedItem(self.size, self.constr, self.number.numberProvider)


class PosConstraint:
    def __init__(self, spacing):
        self.spacing = spacing
        self.xShift = 0
        self.yShift = 0

    def __call__(self, pnt):
        if self.spacing == 1:
            return pnt

        ix = int(pnt.x()) - self.xShift
        iy = int(pnt.y()) - self.yShift
        x = (ix / self.spacing) * self.spacing + self.xShift
        # if ix % self.spacing >= 5:
        #     x += self.spacing
        y = (iy / self.spacing) * self.spacing + self.yShift
        # if iy % self.spacing >= 5:
        #     y += self.spacing

        return QPointF(x, y)


class ImageScene(QGraphicsScene):

    def __init__(self, imageUrl=None):
        QGraphicsScene.__init__(self)
        self.imgItem = None
        self.gridLines = []
        self.gridXShift = 0
        self.gridYShift = 0

        self.posConstr = PosConstraint(10)

        self.pressPos = None
        self.draggingItems = dict()
        self.recentPos = QPointF()

        if imageUrl:
            self.setImage(imageUrl)

        self.userItems = []

    def selectedElements(self):
        return [item for item in self.selectedItems() if item.parentItem() == self.imgItem]

    def setSpacing(self, spacing):
        self.posConstr.spacing = spacing
        self.updateGrid()

    def setXGridShift(self, shift):
        self.posConstr.xShift = shift
        self.updateGrid()

    def setYGridShift(self, shift):
        self.posConstr.yShift = shift
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
        spacing = self.posConstr.spacing

        for i in self.gridLines:
            self.removeItem(i)
            del i
        self.gridLines = []

        if spacing == 1:
            return

        color = QColor(100, 100, 100, 20)

        x = self.posConstr.xShift
        while x <= w:
            item = QGraphicsLineItem(x, 0, x, h)
            item.setPen(color)
            item.setParentItem(self.imgItem)
            self.gridLines.append(item)
            x += spacing

        y = self.posConstr.yShift
        while y <= h:
            item = QGraphicsLineItem(0, y, w, y)
            item.setParentItem(self.imgItem)
            item.setPen(color)
            self.gridLines.append(item)
            y += spacing

    def _add_and_position_element(self, item):
        if not self.imgItem:
            raise ValueError('Image must be set before adding elements')
        r = self.sceneRect()
        item.setPos(r.width() / 2, r.height() / 2)
        item.setParentItem(self.imgItem)
        self.userItems.append(item)
        return item

    def addNumberElement(self, numberProvider):
        return self._add_and_position_element(NumberItem(numberProvider, self.posConstr))

    def addRectElement(self):
        return self._add_and_position_element(RectSelectionItem(QSizeF(100, 50), self.posConstr))

    def addEllipseElement(self):
        return self._add_and_position_element(EllipseSelectionItem(QSizeF(50, 50), self.posConstr))

    def addNumberedRectElement(self, numberProvider):
        return self._add_and_position_element(RectNumberedItem(QSizeF(100, 50), self.posConstr, numberProvider))

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

        add_ellipse = QPushButton()
        add_ellipse.setIcon(icons.get('ellipse'))
        add_ellipse.setToolTip('Add Ellipse')
        add_ellipse.clicked.connect(self.scene.addEllipseElement)

        add_number = QPushButton()
        add_number.setToolTip('Add number')
        add_number.setIcon(icons.get('add_number'))
        add_number.clicked.connect(lambda: self.scene.addNumberElement(self))

        add_numbered_rect = QPushButton()
        add_numbered_rect.setToolTip('Add numbered rectangle')
        add_numbered_rect.setIcon(icons.get('add_numbered_rect'))
        add_numbered_rect.clicked.connect(lambda: self.scene.addNumberedRectElement(self))

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


        spacing = QLineEdit()
        spacing.setText(str(self.scene.posConstr.spacing))
        spacing.setValidator(QIntValidator(bottom=1))
        spacing.returnPressed.connect(lambda: self.scene.setSpacing(int(spacing.text())))
        spacing.setMaximumWidth(30)

        xshift = QSpinBox()
        xshift.setValue(self.scene.posConstr.xShift)
        xshift.valueChanged.connect(lambda v: self.scene.setXGridShift(v))

        yshift = QSpinBox()
        yshift.setValue(self.scene.posConstr.yShift)
        yshift.valueChanged.connect(lambda v: self.scene.setYGridShift(v))

        lt = QHBoxLayout()
        lt.addWidget(add_rect)
        lt.addWidget(add_ellipse)
        lt.addWidget(add_number)
        lt.addWidget(add_numbered_rect)
        lt.addSpacing(20)
        lt.addWidget(duplicate_button)
        lt.addSpacing(20)
        lt.addWidget(delete_button)
        lt.addStretch()
        lt.addWidget(QLabel('Grid Spacing'))
        lt.addWidget(spacing)
        lt.addWidget(QLabel('X Grid Shift'))
        lt.addWidget(xshift)
        lt.addWidget(QLabel('Y Grid Shift'))
        lt.addWidget(yshift)

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


# def main():
#     from pyqode.qt.QtWidgets import QApplication
#     import sys
#
#     app = QApplication(sys.argv)
#     win = EditImageWindow("/home/wgryglas/test-edit.png")
#     win.show()
#
#
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     main()