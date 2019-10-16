import sys
from errors import ConsoleLogger
from utils import PropertiesGetDelegator


class ColorScheme:
    defualt = 1
    darcula = 2

    @staticmethod
    def fromString(text):
        if text == 'darcula':
            return ColorScheme.darcula
        else:
            return ColorScheme.defualt


class SettingsProperty:
    def __init__(self, name, value, typeName):
        self.name = name
        self.value = value
        self.type = typeName

    def appendAsTextNode(self, dom, parent):
        node = dom.createTextNode(str(self.value))
        parent.appendChild(node)

    @staticmethod
    def getStr(node):
        from xml.dom.minidom import Text
        print node.attributes['name'].value

        if isinstance(node, Text):
            return str(node.data.strip())
        else:
            if node.firstChild is not None:
                return str(node.firstChild.nodeValue)
            else:
                return ''


class StringProperty(SettingsProperty):
    def __init__(self, name, value):
        SettingsProperty.__init__(self, name, value, 'str')

    def loadFromNode(self, propNode):
        self.value = SettingsProperty.getStr(propNode)


class BoolProperty(SettingsProperty):
    def __init__(self, name, value):
        SettingsProperty.__init__(self, name, value, 'bool')

    def loadFromNode(self, propNode):
        self.value = bool(SettingsProperty.getStr(propNode))


class IntProperty(SettingsProperty):
    def __init__(self, name, value):
        SettingsProperty.__init__(self, name, value, 'int')

    def loadFromNode(self, propNode):
        self.value = int(SettingsProperty.getStr(propNode))


class FloatProperty(SettingsProperty):
    def __init__(self, name, value):
        SettingsProperty.__init__(self, name, value, 'float')

    def loadFromNode(self, propNode):
        self.value = float(SettingsProperty.getStr(propNode))


class SchemeProperty(SettingsProperty):
    def __init__(self, name, value):
        SettingsProperty.__init__(self, name, value, 'color-scheme')

    def loadFromNode(self, propNode):
        self.value = int(SettingsProperty.getStr(propNode))


class StringList(SettingsProperty):
    def __init__(self, name, value):
        SettingsProperty.__init__(self, name, value, 'str-list')

    def loadFromNode(self, propNode):
        from xml.dom.minidom import Text
        self.value = [str(node.firstChild.nodeValue) for node in propNode.childNodes if not isinstance(node, Text)]

    def appendAsTextNode(self, dom, propNode):
        for text in self.value:
            outerNode = dom.createElement('str')
            textNode = dom.createTextNode(text)
            outerNode.appendChild(textNode)
            propNode.appendChild(outerNode)


class PropertiesHandler:
    propertyTag = 'property'

    def __init__(self, nodeName, logger=ConsoleLogger()):
        self.props = {}
        self.nodeName = nodeName
        self.logger = logger

    def __getattr__(self, item):
        return self.props[item].value

    def add(self, prop):
        self.props[prop.name] = prop

    def str(self, name, value):
        self.add(StringProperty(name, value))

    def int(self, name, value):
        self.add(IntProperty(name, value))

    def bool(self, name, value):
        self.add(BoolProperty(name, value))

    def float(self, name, value):
        self.add(FloatProperty(name, value))

    def colorScheme(self, name, value):
        self.add(SchemeProperty(name, value))

    def strList(self, name, array):
        self.add(StringList(name, array))

    def load(self, miniXmlDom):
        root = miniXmlDom.getElementsByTagName(self.nodeName)
        if len(root) > 1:
            raise Exception('Your settings should contain only one <settings> node')
        root = root[0]

        for propNode in root.getElementsByTagName(self.propertyTag):
            prop = self.props[propNode.attributes['name'].value]
            if prop:
                prop.loadFromNode(propNode)
            else:
                self.logger.wraning('Found {} in settings file but this property is not used by application')

    def save(self, miniXmlDom):
        group = miniXmlDom.createElement(self.nodeName)
        for propName in self.props:
            prop = self.props[propName]
            pNode = miniXmlDom.createElement(self.propertyTag)
            pNode.setAttribute('name', prop.name)
            pNode.setAttribute('type', prop.type)
            prop.appendAsTextNode(miniXmlDom, pNode)
            group.appendChild(pNode)

        miniXmlDom.appendChild(group)


class AppSettings(PropertiesGetDelegator):

    def __init__(self):
        self.properties = PropertiesHandler('settings')
        self.properties.str('sort_images', 'date')
        self.properties.bool('relative_paths', True)
        self.properties.str('figure_width', '400 px')
        self.properties.str('editor_font', '')
        self.properties.colorScheme('color_scheme', ColorScheme.defualt)
        self.properties.bool('sync_scrolling', True)
        self.properties.int('content_refresh_time', 1000)
        self.properties.strList('recent', ['/home/wgryglas/python/pelicanDoc', '/home/wgryglas/Code/Python/pelicanReDoc'])

        PropertiesGetDelegator.__init__(self, self.properties)

    def get(self, name):
        return self.properties.props[name].value

    def set(self, name, value):
        self.properties.props[name].value = value

    @property
    def recent_existing(self):
        from os.path import exists
        return filter(lambda d: exists(d), self.recent)

    def loadFromFile(self, path):
        from xml.dom.minidom import parse
        from os.path import exists
        if exists(path):
            dom = parse(path)
            self.properties.load(dom)

    def saveToFile(self, path):
        from xml.dom.minidom import Document
        dom = Document()
        self.properties.save(dom)
        with open(path, 'w+') as xmlFile:
            dom.writexml(xmlFile, addindent='\t', newl='\n')


class SystemSettings(PropertiesGetDelegator):

    file_template_dir_name = 'fileTemplates'
    project_template_dir_name = 'projectTemplates'

    def __init__(self):
        from os.path import sep
        platformName = sys.platform
        if platformName.startswith('linux'):
            os = Linux()
        elif platformName.startswith('win'):
            os = Windows()
        else:
            raise Exception('Your OS is not supported')

        self.sep = sep

        PropertiesGetDelegator.__init__(self, os)

    @property
    def isInitialized(self):
        import os
        return os.path.exists(self.userSettingsDir)

    def loadSettings(self):
        settings = AppSettings()
        if self.isInitialized:
            settings.loadFromFile(self.settingsFilePath)
        return settings

    def saveSettings(self, settings):
        settings.saveToFile(self.os.settingsFilePath)

    def createShortcut(self):
        pass

    def createUserDir(self):
        from os import makedirs
        makedirs(self.userSettingsDir)

    @property
    def templetesDirPath(self):
        return self.userSettingsDir + self.sep + self.file_template_dir_name

    @property
    def templateFiles(self):
        from os import walk, sep
        p, dirs, files = walk(self.templetesDirPath).next()
        return [p + sep + f for f in files]


class Linux:
    def __init__(self):
        from os.path import expanduser
        home = expanduser("~")
        self.userSettingsDir = '{}/.reWriter'.format(home)

    @property
    def settingsFilePath(self):
        return '{}/settings.xml'.format(self.userSettingsDir)


class Windows:
    pass