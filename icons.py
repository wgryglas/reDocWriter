
from pyqode.qt.QtWidgets import QPixmap, QIcon
import os


_icons_path_ = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep + 'assets' + os.sep + 'icons'


def _load_icon_(name):
    i = QIcon()
    i.addPixmap(QPixmap(_icons_path_ + os.sep + name + '.png'))
    return i


def screenshot():
    return _load_icon_('screenshot')

def webbrowser():
    return _load_icon_('webbrowser')

def get(name):
    return _load_icon_(name)