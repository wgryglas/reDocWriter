from git import Repo
import os, subprocess
from errors import ErrorHandler
from files import *
from async import start_process

from pyqode.qt.QtCore import Signal, QObject


class BaseWebsiteBuildEnvironment:
    rst_location = "content"
    theme_location = "theme"
    output_location = "output"
    server_port = "8000"

    def __init__(self, local_repository_path):
        self.repository_path = local_repository_path
        self.server_process = None

    def run_output_http_server(self):
        """
        runs http server inside separate system process. If server is already running
        it will be killed first and than new process started
        :return: None
        """
        if self.server_process:
            self.server_process.kill()
        self.server_process = subprocess.Popen(['invoke', 'serve'], cwd=self.repository_path)

    def build_website(self, onSuccess, onError):
        """
        Renders html from current sources
        :param onSuccess:
        :param onError:
        :return:
        """
        # return subprocess.Popen(['invoke', 'build'], cwd=self.repository_path, stdout=subprocess.PIPE,
        #                         stderr=subprocess.STDOUT)
        start_process(onSuccess, onError, self.repository_path, ['invoke', 'build'])

    def rebuild_file(self, relative_file_path):
        """
        :param relative_file_path: relative path in RST containing folder
        :return:
        """

    def get_figures_folder_path_for(self, local_file_path):
        """
        :param local_file_path:
        :return: str, local path to folder containing images for provided source
        """
        import os
        local_file_path = path_without_in_place_dot(local_file_path)
        paths = local_file_path.split(os.sep)
        paths[-1] = paths[-1].split('.')[0]
        result = ['figures']
        result.extend(paths)
        return os.sep.join(result)

    @property
    def sources_root_path(self):
        return self.repository_path + os.sep + self.rst_location

    def source_full_path(self, source_local_path):
        return self.repository_path + os.sep + self.rst_location + os.sep + source_local_path

    # def source_figures_path(self, source_local_path):
    #     return self.

    def __del__(self):
        if self.server_process:
            self.server_process.kill()


class GitRepository:
    def __init__(self, local_path):
        self._repo_ = Repo(local_path)

    @property
    def root_path(self):
        return self._repo_.working_tree_dir

    def isValid(self):
        return not self._repo_.bare

    def isModified(self):
        return self._repo_.is_dirty()

    def getModifiedFiles(self):
        return self._repo_.untracked_files

    def revertLocalChanges(self):
        pass

    def updateFromRemote(self):
        pass

    def create_commit(self, message):
        pass
        # self.gitRepo.

    def stage_all_modified(self):
        pass

    def stage_file(self, repository_file_path):
        pass

    def push(self, origin_name=None):
        # origin = self._repo_.head if not origin_name else self._repo_.heads[origin_name]
        # origin.push()
        pass

    def pull(self):
        pass


class Session(QObject):
    html_output_changed = Signal()
    html_content_changed = Signal()
    content_changed = Signal(str)
    error_raised = Signal(str)

    # active_file_changed = Signal()

    def __init__(self, project_root, errors=ErrorHandler(), **kwargs):
        QObject.__init__(self)

        #self._settings_ = settins

        self._root_ = project_root

        self._env_ = BaseWebsiteBuildEnvironment(project_root) if 'config' not in kwargs else kwargs['config']

        self._errors_ = errors

        self._repo_ = GitRepository(project_root)
        if not self._repo_.isValid():
            errors.show("Provided path is not a valid git repository")
            raise Exception("Wrong Path to Git Repository")

        self._active_file_ = ""
        self._content_ = ""

        self.error_raised.connect(errors.show)


    @property
    def active_local_path(self):
        return self._active_file_

    @property
    def active_full_path(self):
        return self._env_.source_full_path(self._active_file_)

    @property
    def is_file_set(self):
        return len(self._active_file_) > 0

    def start_local_server(self):
        """
        Starts local server providing html files.
        :return: root address for local server
        """
        self._env_.run_output_http_server()
        return "http://localhost:{}/".format(self._env_.server_port)

    def get_sources_structure(self):
        """
        Looks for RST source files for generating data
        :return: Files Tree
        """
        return create_file_tree(self._env_.sources_root_path)

    @property
    def active_file_figures_folder(self):
        root = self.get_sources_structure()
        figures_folder_path = self._env_.get_figures_folder_path_for(self._active_file_)
        figures_folder_full_path = self._env_.source_full_path(figures_folder_path)
        return root.find_folder_by_path(figures_folder_full_path)

    def get_figures_files_for(self, local_file_path):
        import os

        figures_folder_path = self._env_.get_figures_folder_path_for(local_file_path)
        figures_folder_full_path = self._env_.source_full_path(figures_folder_path)

        if not os.path.exists(figures_folder_full_path):
            self._errors_.show('Figures folder for {} source file does not exist.\n'
                               'Make sure that {} path exist'.format(local_file_path, figures_folder_full_path))
            return []

        if not os.path.isdir(figures_folder_full_path):
            self._errors_.show('{} is not directory.\n'
                               'The path should store images for {} for *.rst source'.
                               format(local_file_path, figures_folder_full_path))
            return []

        root = self.get_sources_structure()
        folder = root.find_folder_by_path(figures_folder_full_path)

        if not folder:
            self._errors_.show("Couldn't find {} path in following sources tree {}".format(figures_folder_full_path, root))
            return []

        figures = filter(lambda f: f.name.endswith('.png') or f.name.endswith('.jpg'), folder.files)

        # root = self.get_sources_structure()
        # dirs = local_file_path.split(os.sep)[:-1]
        #
        # if dirs[0] == '.':
        #     if len(dirs) > 1:
        #         dirs = dirs[1:]
        #     else:
        #         dirs = []
        #
        # parent = root
        # for d in dirs:
        #     for f in parent.folders:
        #         if f.name == d:
        #             parent = f
        #             break
        #
        # if len(dirs) == 0:
        #     dirs = ['.']
        #
        # if parent.local_path != os.sep.join(dirs):
        #     msg = 'Wrong path {} while listing file source images'.format(local_file_path)
        #     self.error_raised.emit(msg)
        #     return []
        #
        # figures = []
        # figfolder = parent.get_child('figures')
        # if figfolder:
        #     file_folder_name = local_file_path.split(os.sep)[-1].split('.')[0]
        #     files_folder = figfolder.get_child(file_folder_name)
        #     if files_folder:
        #         figures = filter(lambda f: f.name.endswith('.png') or f.name.endswith('.jpg'), files_folder.files)

        return figures

    def set_active_file(self, source_file_location):
        """
        Sets RST file content and updates html file related to providede source
        :param source_file_location:
        :return:
        """
        if self.is_file_set:
            self.save_active_file()
        self._active_file_ = source_file_location
        self._load_active_file_content_()
        self.html_output_changed.emit()

    def get_active_file_content(self):
        return self._content_

    def set_active_file_content(self, content):
        if not self.is_file_set:
            return
        self._content_ = content
        self.save_active_file()
        self.update_website()


    def render_active_file(self):
        """
        :return: HTML String
        """
        pass

    def get_file_output(self, local_file_path):
        import re, os
        full_path = self._env_.source_full_path(local_file_path)

        if not os.path.exists(full_path):
            self._errors_.show("Can't provide html output file because source {} does not exist")
            return None

        with open(full_path, 'r') as f:
            for l in f:
                if l.strip().startswith(':slug:'):
                    name = re.findall(r'\s*:slug:\s*([\w|-]+)\s*', l)[0]
                    return self._root_ + os.sep + self._env_.output_location + os.sep + name + '.html'

        return None

    @property
    def active_file_output(self):
        return self.get_file_output(self._active_file_)

    def update_website(self):
        def handle_success(result):
            print result
            self.html_content_changed.emit()

        def handle_error(error):
            print error
            self.error_raised.emit("Couldn't render html\n" + error)

        self._env_.build_website(handle_success, handle_error)

    def save_active_file(self):
        with open(self.active_full_path, 'w') as f:
            f.write(self._content_)

    def _load_active_file_content_(self):
        with open(self.active_full_path, 'r') as f:
            self._content_ = ''.join(f.readlines())
            self._file_is_up_to_date_ = True
            self.content_changed.emit(self._content_)
