import docutils
import mimetypes as mimes
import sys, os
from pyqode.core import api, modes, panels
from pyqode.rst.backend import server, workers

from pyqode.rst import modes as rstmodes

import rst_server as server
import rst_workers as workers


class RstCodeEdit(api.CodeEdit):
    """
    Require custom CodeEdit to handle custom
    roles and derictives in Error Checkeer

    This is copy paste from original pyqode.rst.code_edit.RstCodeEdit
    The key was to define custom roles in this file, otherwise could not
    make Error Checker see custom roles. Custom roles are define in standard way
    under the docutils framework
    """
    # generic
    mimetypes = ['text/x-rst']

    for m in mimetypes:
        mimes.add_type(m, '.rst')


    # server next to app exe path when frozen
    #DEFAULT_SERVER = server.__file__ if not hasattr(sys, 'frozen') else os.path.dirname(sys.executable) + os.sep + 'server'

    # server boundled in one exe path when frozen
    DEFAULT_SERVER = server.__file__ if not hasattr(sys, 'frozen') else os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep + 'server'

    # This is very important for frozen type application, as server script is run as an external process. Therfore
    # when whole app is boundled as frozen backend.start will try to run server script as a program or if will not
    # figure out that it is program it will execute it as a script using sys.executable as interpreter pointing to
    # frozen app exe file ---> lauching the app once again.
    # To overcome this the backend.start function must get server_script without *.py extension and sys must have
    # 'frozen' attribute which is added when app is executed from boundle. So here we must make sure that we will
    # provide path to executable file not python script to force BackendManager run the

    def __init__(self, parent=None, server_script=None,
                 interpreter=sys.executable, args=None,
                 create_default_actions=True, color_scheme='qt',
                 reuse_backend=True):

        super(RstCodeEdit, self).__init__(parent, create_default_actions)

        if server_script is None:
            server_script = self.DEFAULT_SERVER

        print 'is freezed?', hasattr(sys, 'frozen')
        print self.DEFAULT_SERVER
        print sys.executable
        print os.getcwd()

        sys.frozen = True

        self.backend.start(server_script, interpreter, args,
                           reuse=reuse_backend)

        # append panels
        self.panels.append(panels.LineNumberPanel())
        self.panels.append(panels.SearchAndReplacePanel(),
                           api.Panel.Position.TOP)

        # append modes
        self.modes.append(modes.CursorHistoryMode())
        self.modes.append(modes.CaseConverterMode())
        self.modes.append(modes.FileWatcherMode())

        # self.modes.append(modes.CaretLineHighlighterMode())

        self.modes.append(modes.RightMarginMode())
        self.modes.append(rstmodes.RstSH(self.document(), color_scheme=api.ColorScheme(color_scheme)))
        self.modes.append(modes.ZoomMode())
        cc = modes.CodeCompletionMode()
        cc.trigger_symbols[:] = []
        self.modes.append(cc)
        self.modes.append(modes.AutoIndentMode())
        self.modes.append(modes.IndenterMode())
        self.modes.append(modes.OccurrencesHighlighterMode())
        self.modes.append(modes.SmartBackSpaceMode())
        self.modes.append(modes.CheckerMode(workers.linter))

        self.panels.append(panels.EncodingPanel(), api.Panel.Position.TOP)
        self.panels.append(panels.ReadOnlyPanel(), api.Panel.Position.TOP)
        self.panels.append(panels.CheckerPanel())

    def setPlainText(self, txt, mime_type='', encoding=''):
        mime_type = self.mimetypes[0]
        try:
            self.syntax_highlighter.set_lexer_from_filename(self.file.path)
        except AttributeError:
            # syntax highlighter removed, e.g. file size > FileManager.limit
            pass
        super(RstCodeEdit, self).setPlainText(txt, mime_type, encoding)

    def to_html(self):
        """
        Return the content of the editor as an html text.
        """
        try:
            return docutils.core.publish_parts(
                self.toPlainText(), source_path=self.file.path,
                writer_name='html', settings_overrides={
                    'output_encoding': 'unicode'})['html_body']
        except docutils.utils.SystemMessage as e:
            return str(e)
