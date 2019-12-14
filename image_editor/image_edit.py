from pyqode.qt.QtCore import Qt, QSizeF, QPointF, Signal, QPoint
from pyqode.qt.QtWidgets import QGraphicsView, QColor, QPainter, QGraphicsScene, QPixmap, QGraphicsLineItem, \
    QMainWindow, QWidget, QPushButton, QSpinBox, QLineEdit, QHBoxLayout, QVBoxLayout, QStyle, QIntValidator, QLabel

from number_item import NumberItem
from rect_items import RectSelectionItem, EllipseSelectionItem, RectNumberedItem


class PosConstraint:
    def __init__(self, spacing):
        self.spacing = spacing
        self.xShift = 0
        self.yShift = 0

    def round(self, val, shift):
        v = val - shift
        return int(v - (v % self.spacing) + shift)

    def __call__(self, pnt):
        if self.spacing == 0:
            return pnt
        return QPointF(self.round(pnt.x(), self.xShift), self.round(pnt.y(), self.yShift))


class DragStyle:
    def __init__(self):
        self.start = QPointF()
        self.pos = QPointF()
        self.posPrev = QPointF()
        self.startItemsPosition = dict()

    def isValid(self, selectedItems, keyModifiers, buttons):
        """
        :param selectedItems:
        :param keys:
        :param buttons:
        :return: True if is applicable to current context
        """
        raise NotImplementedError()

    def _filterItems_(self, selectedItems, keys, buttons):
        # The only item without parent is the root image, we need to get rid of it from selection
        return filter(lambda e: e.parentItem(), selectedItems)

    def initDrag(self, selectedItems, keys, buttons):
        """
        Inits current drag, possibly modifies list of object that should be processed
        :param selectedItems:
        :param keys:
        :param buttons:
        :return: a new list of items that would be affected by drag events
        """
        filtered = self._filterItems_(selectedItems, keys, buttons)
        for item in filtered:
            self.startItemsPosition[item] = item.pos()
        return filtered

    def setStartPoint(self, pnt):
        self.start = pnt
        self.pos = pnt
        self.posPrev = pnt

    def setMovePoint(self, pnt):
        self.posPrev = self.pos
        self.pos = pnt

    def applyDrag(self, items):
        raise NotImplementedError()

    def finish(self):
        self.startItemsPosition = dict()


class DefaultDrag(DragStyle):

    def _filterItems_(self, selectedItems, keys, buttons):
        return filter(lambda e: e.isFreeMovable(), DragStyle._filterItems_(self, selectedItems, keys, buttons))

    def isValid(self, selectedItems, keyModifiers, buttons):
        return len(selectedItems) == 1 and keyModifiers == Qt.NoModifier and buttons == Qt.LeftButton

    def applyDrag(self, items):
        bigDelta = self.pos - self.start
        delta = self.pos - self.posPrev
        for item in items:
            item.dragMove(delta, bigDelta)


class DuplicateDrag(DragStyle):
    def __init__(self, scene):
        DragStyle.__init__(self)
        self.scene = scene
        self.dragging = None
        self.dir = None

    def isValid(self, selectedItems, keyModifiers, buttons):
        return len(selectedItems) > 0 and keyModifiers == Qt.ControlModifier and buttons == Qt.LeftButton

    def clone(self):
        self.dragging = [e.clone() for e in self.scene.selectedElements()]
        for e in self.dragging:
            self.scene.addUserItem(e)

    def setStartPoint(self, pnt):
        DragStyle.setStartPoint(self, pnt)

    def setMovePoint(self, pnt):
        DragStyle.setMovePoint(self, pnt)
        if not self.dragging:
            self.clone()

        if not self.dir:
            delta = self.pos - self.posPrev
            if delta.x() != 0 or delta.y() != 0:
                self.dir = 1 if abs(delta.x()) > abs(delta.y()) else 2

    def finish(self):
        self.dragging = None
        self.dir = None

    def applyDrag(self, items):
        if self.dragging and self.dir:
            bigDelta = self.pos - self.start
            delta = self.pos - self.posPrev
            delta = QPointF(delta.x(), 0) if self.dir == 1 else QPointF(0, delta.y())
            for item in self.dragging:
                item.dragMove(delta, bigDelta)


# class SceneMouseEvent:
#     def __init__(self, buttons, modifier, pos, scenePos):

class ImageScene(QGraphicsScene):
    on_item_edit = Signal(object)

    def __init__(self, imageUrl=None):
        QGraphicsScene.__init__(self)
        self.imgItem = None
        self.gridLines = []
        self.gridXShift = 0
        self.gridYShift = 0

        self.posConstraint = PosConstraint(0)

        self.pressPos = None
        self.draggingItems = dict()
        self.recentPos = QPointF()

        if imageUrl:
            self.setImage(imageUrl)

        self.userItems = []

        self.dragStyles = [DefaultDrag(), DuplicateDrag(self)]

        self.activeDragStyle = None

        self.dragItems = []

        self._is_pick_enabled_ = True

        self.editedItem = None

        self.pressEvent = False
        self.dragStarted = False

    def setPickEnabled(self, flag):
        self._is_pick_enabled_ = flag

    def processPickEvent(self, event):
        if not self._is_pick_enabled_:
            event.ignore()
            return False
        else:
            return True

    def selectedElements(self):
        return [item for item in self.selectedItems() if item.parentItem() == self.imgItem]

    def setSpacing(self, spacing):
        self.posConstraint.spacing = spacing
        self.updateGrid()

    def setXGridShift(self, shift):
        self.posConstraint.xShift = shift
        self.updateGrid()

    def setYGridShift(self, shift):
        self.posConstraint.yShift = shift
        self.updateGrid()

    def setImage(self, url):
        if self.imgItem:
            self.removeItem(self.imgItem)
            del self.imgItem

        pxm = QPixmap(url)

        self.imgItem = self.addPixmap(pxm)
        # from pyqode.qt.QtWidgets import QGraphicsItem
        # self.imgItem.setFlags(QGraphicsItem.ItemIsSelectable)

        # if image should be displayied with antialiasing when zoomed
        # self.imgItem.setTransformationMode(Qt.SmoothTransformation)
        self.updateGrid()

    def updateGrid(self):
        rect = self.sceneRect()#self.imgItem.boundingRect()
        w = rect.width()
        h = rect.height()
        spacing = self.posConstraint.spacing

        for i in self.gridLines:
            self.removeItem(i)
            del i
        self.gridLines = []

        if spacing == 0:
            return

        color = QColor(100, 100, 100, 20)

        def setupLine(l):
            l.setPen(color)
            l.setFlag(QGraphicsLineItem.ItemIsSelectable, False)
            l.setFlag(QGraphicsLineItem.ItemAcceptsInputMethod, False)

        x = self.posConstraint.xShift
        while x <= w:
            item = QGraphicsLineItem(x, 0, x, h)
            item.setParentItem(self.imgItem)
            setupLine(item)
            self.gridLines.append(item)
            x += spacing

        y = self.posConstraint.yShift
        while y <= h:
            item = QGraphicsLineItem(0, y, w, y)
            item.setParentItem(self.imgItem)
            setupLine(item)
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
        return self._add_and_position_element(NumberItem(numberProvider, self.posConstraint))

    def addRectElement(self):
        return self._add_and_position_element(RectSelectionItem(QSizeF(100, 50), self.posConstraint))

    def addEllipseElement(self):
        return self._add_and_position_element(EllipseSelectionItem(QSizeF(50, 50), self.posConstraint))

    def addNumberedRectElement(self, numberProvider):
        return self._add_and_position_element(RectNumberedItem(QSizeF(100, 50), self.posConstraint, numberProvider))

    def addUserItem(self, item):
        """
        :param item: instance derived from ItemBase
        :return:
        """
        item.setParentItem(self.imgItem)
        self.userItems.append(item)

    def duplicateSelection(self):
        newEl = [e.clone() for e in self.selectedElements()]
        self.clearSelection()
        for e in newEl:
            self.addUserItem(e)

        for e in reversed(newEl):
            if e.isEditable():
                self.setItemEdited(e)
                return

    def _get_click_items(self, event):
        clickItems = self.items(event.scenePos())
        if self.imgItem in clickItems:
            clickItems.remove(self.imgItem)

        for it in clickItems:
            if it in self.gridLines:
                clickItems.remove(it)

        return clickItems

    def setItemEdited(self, item):
        if self.editedItem:
            self.editedItem.setEdited(False)
        item.setEdited(True)
        self.editedItem = item

    def mouseDoubleClickEvent(self, e):
        if self.processPickEvent(e):
            clickItems = self._get_click_items(e)
            if len(clickItems) == 1 and clickItems[0].isEditable():
                item = clickItems[0]
                self.setItemEdited(item)
                self.on_item_edit.emit(item)

    def mousePressEvent(self, e):
        QGraphicsScene.mousePressEvent(self, e)

        pressItems = self._get_click_items(e)
        if len(pressItems) == 0 and e.buttons() == Qt.LeftButton:
            self.emptyPress()
        elif self.processPickEvent(e):
            print 'setting press event'
            from pyqode.qt.QtWidgets import QMouseEvent
            self.pressEvent = True#QMouseEvent(e.type(), e.pos(), e.globalPos(), e.button(), e.buttons(), e.modifiers())

    def mouseMoveEvent(self, event):
        if not self.processPickEvent(event):
            QGraphicsScene.mouseMoveEvent(self, event)
            return

        QGraphicsScene.mouseMoveEvent(self, event)

        if self.pressEvent:
            if not self.dragStarted:
                #startEvent = self.pressEvent
                self.draggingItems = dict()
                selItems = self.selectedItems()
                styles = filter(lambda s: s.isValid(selItems, event.modifiers(), event.buttons()), self.dragStyles)
                if len(styles) > 1:
                    raise ValueError('More then single drag style detected')
                elif len(styles) == 0:
                    return

                style = styles[0]
                self.activeDragStyle = style

                self.dragItems = style.initDrag(selItems, event.modifiers(), event.buttons())
                for item in self.dragItems:
                    item.setDragged(True)
                    item.dragStart(event.lastScenePos())

                style.setStartPoint(event.lastScenePos())

                self.dragStarted = True
                print "drag started"

            if self.activeDragStyle:
                p = event.scenePos()
                self.activeDragStyle.setMovePoint(p)
                self.activeDragStyle.applyDrag(self.dragItems)

        # TODO Force redraw, this would give worse performance, but ensures proper visual effect
        self.update(self.sceneRect())

    def mouseReleaseEvent(self, e):
        if not self.processPickEvent(e):
            QGraphicsScene.mouseReleaseEvent(self, e)
            return

        QGraphicsScene.mouseReleaseEvent(self, e)

        for item in self.dragItems:
            item.setDragged(False)
            item.dragEnd()

        self.dragItems = []

        if self.activeDragStyle:
            self.activeDragStyle.finish()
            self.activeDragStyle = None

        self.pressEvent = None
        self.dragStarted = False

    def updateViewScale(self, scale):
        from item_base import ItemBase
        for item in self.items():
            if isinstance(item, ItemBase):
                item.setSizeScale(scale)

    def emptyPress(self):
        if self.editedItem:
            self.editedItem.setEdited(False)
            self.editedItem = None
            self.on_item_edit.emit(None)

    def renderToFile(self, path):
        from pyqode.qt.QtGui import QImage

        for line in self.gridLines:
            line.setVisible(False)

        self.clearSelection()
        self.emptyPress()

        for i in self.userItems:
            i.forceDefaultStyle(True)

        self.setSceneRect(self.itemsBoundingRect())

        image = QImage(self.sceneRect().size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        # painter.setRenderHint(QPainter.Antialiasing, True)
        # painter.setRenderHint(QPainter.TextAntialiasing, True)
        self.render(painter)
        painter.end()

        image.save(path)

        for line in self.gridLines:
            line.setVisible(True)

        for i in self.userItems:
            i.forceDefaultStyle(False)

    def deleteSelected(self):
        for e in self.selectedElements():
            self.removeItem(e)
            del e


class ImageCanvas(QGraphicsView):

    def __init__(self, *args):
        QGraphicsView.__init__(self, *args)
        self._restore_default_drag_mode_()
        self.is_translating = False
        self.imgScene = args[0]

        self.startPoint = None
        self.startScrollValues = None

    def isTranslating(self):
        return self.is_translating

    def setTranslating(self, flag):
        self.is_translating = flag
        self.imgScene.setPickEnabled(not flag)

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.scale(1.25, 1.25)
        else:
            self.scale(0.8, 0.8)
        self.scene().updateViewScale(1.0 / self.transform().m11())

    def _restore_default_drag_mode_(self):
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def mousePressEvent(self, event):
        self.scene().pressEvaluated = False
        if event.buttons() == Qt.MidButton:
            self.setTranslating(True)
            self.setCursor(Qt.ClosedHandCursor)
            self.startScrollValues = QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
            self.startPoint = event.pos()
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.isTranslating():
            self.setTranslating(False)
            self.setCursor(Qt.ArrowCursor)
        QGraphicsView.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.isTranslating():
            self.horizontalScrollBar().setValue(self.startScrollValues.x() - (event.x() - self.startPoint.x()))
            self.verticalScrollBar().setValue(self.startScrollValues.y() - (event.y() - self.startPoint.y()))
            event.accept()
        else:
            QGraphicsView.mouseMoveEvent(self, event)

    @property
    def VIEW_CENTER(self):
        return self.viewport().rect().center()

    @property
    def VIEW_WIDTH(self):
        return self.viewport().rect().width()

    @property
    def VIEW_HEIGHT(self):
        return self.viewport().rect().height()

    def saveWidgetAs(self, path):
        self.scene().deselectAll()
        self.fitInView()
        self.scene().renderToFile(path)
        #QPixmap.grabWidget(self).save(path)


class EditImageWindow(QMainWindow):
    on_saved = Signal()
    on_exit = Signal()

    editStyle = '''
        QLineEdit { border-radius:10px; border: 1px solid gray; padding-left:5px; padding-right:5px}
        QLineEdit:focus { border: 1.5px solid lightblue; padding-left:5px; padding-right:5px}
    '''

    def __init__(self, path):
        QMainWindow.__init__(self)
        self.path = path
        self.scene = ImageScene(imageUrl=path)
        self.view = ImageCanvas(self.scene)
        self.leftPanel = self.configureOverlyPanel(QWidget())
        self.editLayout = QVBoxLayout()
        self.editLayout.setSpacing(0)
        self.leftPanel.setLayout(self.editLayout)
        self.leftPanel.setVisible(False)

        self.numberIter = 1

        self.enabledOnSelection = []

        self.do_layout()

        self.scene.selectionChanged.connect(self.update_enabled)

        self.scene.on_item_edit.connect(self.showProperties)

    def nextNumber(self):
        v = self.numberIter
        self.numberIter += 1
        return v

    def update_enabled(self):
        sel = len(self.scene.selectedElements()) > 0
        for button in self.enabledOnSelection:
            button.setEnabled(sel)

    def configureOverlyPanel(self, widget):
        widget.setStyleSheet('''
                             QWidget {
                                 background-color:white;
                                 border-radius:10px;
                             }
                            ''')
        # widget.setAutoFillBackground(True)
        # widget.setAttribute()
        from pyqode.qt.QtWidgets import QGraphicsDropShadowEffect
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setXOffset(0)
        effect.setYOffset(0)
        widget.setGraphicsEffect(effect)
        widget.setVisible(False)
        return widget

    def showProperties(self, item):

        for i in reversed(range(self.editLayout.count())):
            self.editLayout.itemAt(i).widget().setParent(None)

        self.leftPanel.setVisible(item is not None)

        if item is None:
            return

        # close = QPushButton('x')
        # close.clicked.connect(lambda: self.scene.emptyPress())
        # l = QHBoxLayout()
        # l.addStretch(1)
        # l.addWidget(close)
        # w = QWidget()
        # w.setLayout(l)
        # self.editLayout.addWidget(w)

        from properties import PropertyWidget
        from widgets import horizontalSeparator, hoverActiveButton

        for p in item.properties():
            rowW = PropertyWidget(item.properties(), p.name)
            rowW.edit.setStyleSheet(EditImageWindow.editStyle)
            rowW.edit.setMaximumWidth(80)
            self.editLayout.addWidget(rowW)

        if isinstance(item, RectSelectionItem):
            insetInput = QLineEdit()
            insetInput.setStyleSheet(EditImageWindow.editStyle)
            insetInput.setValidator(QIntValidator())
            insetInput.setMaximumWidth(40)
            insetInput.setText('1')
            insetInput.setTextMargins(6, 0, 0, 0)
            rowLt = QHBoxLayout()
            bt = hoverActiveButton("Insert Insets")
            bt.clicked.connect(lambda: self.appendInsets(int(insetInput.text()), item))

            rowLt.addWidget(insetInput)
            rowLt.addStretch(10)
            rowLt.addWidget(bt)
            panel = QWidget()
            panel.setLayout(rowLt)


            self.editLayout.addWidget(horizontalSeparator())
            self.editLayout.addWidget(panel)

    def appendInsets(self, insets, item):
        p = item.pos()
        s = item.size
        item.setRect(p.x()-insets, p.y()-insets, s.width()+2*insets, s.height()+2*insets)

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
        spacing.setText(str(self.scene.posConstraint.spacing))
        spacing.setValidator(QIntValidator(bottom=0))
        spacing.returnPressed.connect(lambda: self.scene.setSpacing(int(spacing.text())))
        spacing.setMaximumWidth(30)

        xshift = QSpinBox()
        xshift.setValue(self.scene.posConstraint.xShift)
        xshift.valueChanged.connect(lambda v: self.scene.setXGridShift(v))

        yshift = QSpinBox()
        yshift.setValue(self.scene.posConstraint.yShift)
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

        topBottom = QVBoxLayout()
        leftToRight = QHBoxLayout()
        leftToRight.addWidget(self.leftPanel)
        leftToRight.addStretch(10)
        topBottom.addStretch(1)
        topBottom.addLayout(leftToRight)
        topBottom.addStretch(1)
        self.view.setLayout(topBottom)

        lt = QVBoxLayout()
        lt.addWidget(bar)
        #lt.addLayout(leftToRight)
        lt.addWidget(self.view)
        panel.setLayout(lt)

        self.setCentralWidget(panel)

    def closeEvent(self, event):
        if len(self.scene.userItems) > 0:
            from pyqode.qt.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, 'Save changes',
                                         "Do you want to save changes?", QMessageBox.Yes,
                                         QMessageBox.No)  # QMessageBox.Cancel,
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
    #win = EditImageWindow("/home/wgryglas/test-edit.png")
    win = EditImageWindow("/home/wgryglas/Downloads/car-17-boundary-conditions-right-turbulence.png")
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
