from git import Repo


class BaseEnvironment:
    rst_location = "content"
    theme_location = "theme"


class GitRepository:

    def __init__(self, local_path):
        self.gitRepo = Repo(local_path)

    def isValid(self):
        return not self.gitRepo.bare


class Session:
    def __init__(self, project_root, errors, **kwargs):
        self._root_ = project_root

        self._env_ = BaseEnvironment() if 'config' not in kwargs else kwargs['config']

        self._repo_ = GitRepository(project_root)
        if not self.repo.isValid():
            errors.show("Provided path is not a valid git repository")
            raise Exception("Wrong Path to Git Repository")

        self._active_file_ = ""
        self._content_ = ""

    def start_local_server(self):
        """
        Starts
        :return: root for local server
        """
        pass

    def get_sources_structure(self):
        """
        Looks for RST source files for generating data
        :return: Files Tree
        """
        pass

    def set_active_file(self, source_file_location):
        """
        Sets RST  file content and updates html file related to providede source
        :param source_file_location:
        :return:
        """
        pass

    def get_active_file_content(self):
        pass

    def set_active_file_content(self, content):
        pass

    def render_active_file(self):
        """
        :return: HTML String
        """
        pass
