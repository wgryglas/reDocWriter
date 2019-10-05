from enum import Enum


class ColorScheme(Enum):
    defualt = 1
    darcula = 2


class AppSettings:
    def __init__(self):
        self.sort_images = 'date' #name
        self.relative_paths = True
        self.figure_width = '400 px'
        self.editor_font = ''
        self.color_scheme = ColorScheme.defualt
        self.sync_scrolloing = True
        self.recent = ['/home/wgryglas/python/pelicanDoc', '/home/wgryglas/Code/Python/pelicanReDoc']

    @property
    def recent_existing(self):
        from os.path import exists
        return filter(lambda d: exists(d), self.recent)
