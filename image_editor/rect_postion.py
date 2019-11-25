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