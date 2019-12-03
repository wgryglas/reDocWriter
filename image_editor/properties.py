from pyqode.qt.QtCore import QObject, Signal, Qt
from pyqode.qt.QtWidgets import QLineEdit, QLabel, QWidget, QHBoxLayout


class Property:
    def __init__(self, name, setFun, getFun):
        self.name = name
        self._setFun_ = setFun
        self._getFun_ = getFun
        self.errorHandler = None

    def __call__(self):
        return self._getFun_()

    def fromString(self, text):
        pass

    def setValue(self, value):
        self._setFun_(value)
        #self._source_.__dict__[self.name] = value


class TypeProperty(Property):
    def __init__(self, name, setFun, getFun, mapFun):
        Property.__init__(self, name, setFun, getFun)
        self.mapFun = mapFun

    def fromString(self, text):
        try:
            self.setValue(self.mapFun(text))
        except:
            if self.errorHandler:
                self.errorHandler()


class IntProperty(TypeProperty):
    def __init__(self, name, setFun, getFun):
        TypeProperty.__init__(self, name, setFun, getFun, int)


class FloatProperty(TypeProperty):
    def __init__(self, name, setFun, getFun):
        TypeProperty.__init__(self, name, setFun, getFun, float)


class StringProperty(TypeProperty):
    def __init__(self, name, setFun, getFun):
        TypeProperty.__init__(self, name, setFun, getFun, lambda v: v)


class SetterObject:
    def __init__(self, name, source):
        self.name = name
        self.source = source

    def __call__(self, value):
        self.source.__dict__[self.name] = value


def ObjectIntProperty(name, sourceObj):
    return IntProperty(name, SetterObject(name, sourceObj), lambda: sourceObj.__dict__[name])


def ObjectFloatProperty(name, sourceObj):
    return FloatProperty(name, SetterObject(name, sourceObj), lambda: sourceObj.__dict__[name])


class ItemProperties(QObject):
    changed = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.list = []

    def append(self, property):
        self.list.append(property)

    def set(self, list):
        self.list = list

    # def __getattr__(self, key):
    #     return next(x for x in self.list if x.name == key)()
    #
    # def __setattr__(self, key, value):
    #     el = next(x for x in self.list if x.name == key)
    #     if el:
    #         el.setValue(value)
    def get(self, propertyName):
        for p in self.list:
            if p.name == propertyName:
                return p
        return None

    def __iter__(self):
        return self.list.__iter__()


class PropertyLineEdit(QLineEdit):
    def __init__(self, propertiesRepo, name):
        QLineEdit.__init__(self)
        self.repo = propertiesRepo
        self.name = name
        # self.textEdited.connect(self.updateProperty)
        self.repo.changed.connect(self.updateText)
        self.updateText()

    def keyReleaseEvent(self, keyEvent):
        QLineEdit.keyReleaseEvent(self, keyEvent)
        if keyEvent.key() == Qt.Key_Enter:
            self.updateProperty(self.text())

    def focusOutEvent(self, *args, **kwargs):
        QLineEdit.focusOutEvent(self, *args, **kwargs)
        self.updateProperty(self.text())

    def updateProperty(self, text):
        self.repo.get(self.name).fromString(text)

    def updateText(self):
        value = str( self.repo.get(self.name)() )
        #check if the same, to prevent update loop
        if self.text() != value:
            self.setText(value)


class PropertyWidget(QWidget):
    def __init__(self, propertiesRepo, propertyName, gap=10, editWidth=100):
        QWidget.__init__(self)
        lt = QHBoxLayout()
        self.label = QLabel(propertyName)
        self.edit = PropertyLineEdit(propertiesRepo, propertyName)
        self.edit.setFixedWidth(editWidth)
        lt.addWidget(self.label)
        lt.addStretch(gap)
        lt.addWidget(self.edit)
        self.setLayout(lt)

