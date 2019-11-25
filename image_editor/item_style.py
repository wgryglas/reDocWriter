from pyqode.qt.QtWidgets import QGraphicsItem, QPen, QColor, QPainter, QPainterPath


def get_or_default(props, name, default):
    return props[name] if name in props else default


class GraphicsStyle:
    def __init__(self, **props):
        self.width = get_or_default(props, 'width', 1)
        self.background_color = get_or_default(props, 'background_color', None)
        self.border_color = get_or_default(props, 'border_color', None)
        self.foreground_color = get_or_default(props, 'foreground_color', QColor(255,255,255))
        self.antialiased = get_or_default(props, 'antialiased', False)

    def derive(self, **kwargs):
        return GraphicsStyle(
            width=get_or_default(kwargs, 'width', self.width),
            background_color=get_or_default(kwargs, 'background_color', self.background_color),
            border_color=get_or_default(kwargs, 'border_color', self.border_color),
            foreground_color=get_or_default(kwargs, 'foreground_color', self.foreground_color),
            antialiased=get_or_default(kwargs, 'width', self.antialiased)
        )


class StateStyles:
    def __init__(self, default_style, **kwargs):
        self._states_ = kwargs
        self._default_ = default_style

    def set_style(self, name, style):
        self._states_[name] = style

    def get_state(self, text):
        if text in self._states_:
            return self._states_[text]
        else:
            return self._default_


class ItemStyles:
    markColor = QColor(100, 136, 255)
    selColor = QColor(80, 110, 200)
    hoverColor = QColor(255, 0, 0)
    disabled = QColor(200, 200, 200)

    def __init__(self, base=None, **kwargs):

        if isinstance(base, GraphicsStyle):
            self._base_style_ = base
        elif len(kwargs) > 0:
            self._base_style_ = GraphicsStyle(**kwargs)
            print self._base_style_.background_color
        else:
            self._base_style_ = GraphicsStyle(border_color=ItemStyles.markColor, width=3)

        self.states = StateStyles(self._base_style_)

        state_colors = {'hover': ItemStyles.hoverColor, 'select': ItemStyles.selColor, 'disable': ItemStyles.disabled}
        for state in state_colors:
            override = dict()
            if self._base_style_.background_color:
                override['background_color'] = state_colors[state]

            if self._base_style_.border_color:
                override['border_color'] = state_colors[state]

            self.set_style(state, **override)

    def get(self, item):
        if item.isEdited():
            return self.states.get_state('edit')
        elif not item.isEnabled():
            return self.states.get_state('disable')
        elif item.isUnderMouse() or item.isDragged():
            return self.states.get_state('hover')
        elif item.isSelected():
            return self.states.get_state('select')
        elif item.hasFocus():
            return self.states.get_state('focus')
        else:
            return self.states.get_state('default')

    def set_style(self, state_name, **properties):
        self.states.set_style(state_name, self._base_style_.derive(**properties))

