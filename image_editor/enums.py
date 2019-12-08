from enum import Enum
from pyqode.qt.QtCore import QPointF


class Frame(Enum):
    Top = 0
    Left = 1
    Bottom = 2
    Right = 3


class RectAnchors(Enum):
    LeftTop = 0
    CenterTop = 1
    RightTop = 2
    RightCenter = 3
    RightBottom = 4
    CenterBottom = 5
    LeftBottom = 6
    LeftCenter = 7

    @staticmethod
    def toLeft(anchor):
        if anchor == RectAnchors.CenterTop:
            return RectAnchors.LeftTop
        elif anchor == RectAnchors.RightTop:
            return RectAnchors.CenterTop
        elif anchor == RectAnchors.CenterBottom:
            return RectAnchors.LeftBottom
        elif anchor == RectAnchors.RightBottom:
            return RectAnchors.CenterBottom
        return anchor

    @staticmethod
    def toRight(anchor):
        if anchor == RectAnchors.LeftTop:
            return RectAnchors.CenterTop
        elif anchor == RectAnchors.CenterTop:
            return RectAnchors.RightTop
        elif anchor == RectAnchors.LeftBottom:
            return RectAnchors.CenterBottom
        elif anchor == RectAnchors.CenterBottom:
            return RectAnchors.RightBottom
        return anchor

    @staticmethod
    def toUp(anchor):
        if anchor == RectAnchors.LeftCenter:
            return RectAnchors.LeftTop
        elif anchor == RectAnchors.LeftBottom:
            return RectAnchors.LeftCenter
        elif anchor == RectAnchors.RightCenter:
            return RectAnchors.RightTop
        elif anchor == RectAnchors.RightBottom:
            return RectAnchors.RightCenter
        return anchor

    @staticmethod
    def toBottom(anchor):
        if anchor == RectAnchors.LeftCenter:
            return RectAnchors.LeftBottom
        elif anchor == RectAnchors.LeftTop:
            return RectAnchors.LeftCenter
        elif anchor == RectAnchors.RightCenter:
            return RectAnchors.RightBottom
        elif anchor == RectAnchors.RightTop:
            return RectAnchors.RightCenter
        return anchor

    @staticmethod
    def positionOnRect(rect, anchor):
        if anchor == RectAnchors.LeftTop:
            return QPointF(rect.x(), rect.y())
        elif anchor == RectAnchors.CenterTop:
            return QPointF(rect.x()+rect.width()/2, rect.y())
        elif anchor == RectAnchors.RightTop:
            return QPointF(rect.x()+rect.width(), rect.y())
        elif anchor == RectAnchors.RightCenter:
            return QPointF(rect.x()+rect.width(), rect.y()+rect.height()/2)
        elif anchor == RectAnchors.RightBottom:
            return QPointF(rect.x()+rect.width(), rect.y()+rect.height())
        elif anchor == RectAnchors.CenterBottom:
            return QPointF(rect.x()+rect.width()/2, rect.y()+rect.height())
        elif anchor == RectAnchors.LeftBottom:
            return QPointF(rect.x(), rect.y()+rect.height())
        elif anchor == RectAnchors.LeftCenter:
            return QPointF(rect.x(), rect.y()+rect.height()/2)

        raise Exception('Anchor value should be 0-7')

    @staticmethod
    def outDir(anchor):
        import numpy as np

        if anchor == RectAnchors.LeftTop:
            return QPointF(-np.sqrt(2)/2, -np.sqrt(2)/2)
        elif anchor == RectAnchors.CenterTop:
            return QPointF(0, -1)
        elif anchor == RectAnchors.RightTop:
            return QPointF(np.sqrt(2)/2, -np.sqrt(2)/2)
        elif anchor == RectAnchors.RightCenter:
            return QPointF(1, 0)
        elif anchor == RectAnchors.RightBottom:
            return QPointF(np.sqrt(2)/2, np.sqrt(2)/2)
        elif anchor == RectAnchors.CenterBottom:
            return QPointF(0, 1)
        elif anchor == RectAnchors.LeftBottom:
            return QPointF(-np.sqrt(2)/2, np.sqrt(2)/2)
        elif anchor == RectAnchors.LeftCenter:
            return QPointF(-1, 0)

        raise Exception('Anchor value should be 0-7')
