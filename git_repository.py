from git import Repo

class GitRepository:
    def __init__(self, local_path):
        self._repo_ = Repo(local_path)

    @property
    def _default_remote_(self):
        return self._repo_.remotes[0]

    @property
    def address(self):
        return self._repo_.remotes[0].urls.next()

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


    def isRemoteUpToDate(self):
        self._default_remote_.update()

