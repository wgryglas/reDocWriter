import os
from utils import creation_date

def dir_path_without_last_sep(path):
    if path.endswith(os.sep):
        return path[:-len(os.sep)]
    else:
        return path


def path_without_in_place_dot(path):
    if path.startswith('./'):
        return path[2:]
    else:
        return path


class FileNode:
    def __init__(self, name, local_path, full_path, parent):
        self.name = name
        self.local_path = local_path
        self.full_path = full_path
        self.parent = parent

    def __str__(self):
        return self.name

    @property
    def is_dir(self):
        return False

    def date(self):
        return creation_date(self.full_path)


class DirNode(FileNode):
    def __init__(self, name, local_path, full_path, parent=None):
        FileNode.__init__(self, name, local_path, full_path, parent)
        self._children_ = []

    def __getitem__(self, item):
        return self._children_[item]

    def append(self, node):
        self._children_.append(node)

    def find_folder_by_path(self, path):
        full_path = dir_path_without_last_sep(self.full_path)
        path = dir_path_without_last_sep(path)

        if self.full_path == path:
            return self

        if self.full_path not in path:
            return None

        current = self
        sub_paths = path[len(full_path)+1:].split(os.sep)
        for processing in sub_paths:
            matching = filter(lambda d: d.name == processing, current.folders)
            if len(matching) != 1:
                return None
            current = matching[0]
            if dir_path_without_last_sep(current.full_path) == path:
                return current

        return None

    @property
    def files(self):
        return filter(lambda f: not f.is_dir, self._children_)

    @property
    def folders(self):
        return filter(lambda f: f.is_dir, self._children_)

    def get_child(self, name):
        for f in self._children_:
            if f.name == name or f.name.split('.')[0] == name:
                return f
        return None

    @property
    def is_dir(self):
        return True

    def walk(self):
        folders = [self]

        while len(folders) > 0:
            processing = folders
            folders = []
            for folder in processing:
                folders.extend(folder.folders)
                yield (folder, folder.files, folder.folders)

    def __str__(self):
        strings = ''
        for parent, files, folders in self.walk():
            strings += parent.full_path + '\n'
            for f in files:
                strings += f.name + '\n'
            for f in folders:
                strings += f.name + '\n'
            strings += "---------------------\n"

        return strings


def create_file_tree(root_directory_path, file_filter=None):
    import os
    root = DirNode(os.path.basename(root_directory_path), '.', root_directory_path)
    dirs = [root]

    while len(dirs) > 0:
        new_dirs = []
        for parent in dirs:
            for name in os.listdir(parent.full_path):
                full_path = parent.full_path + os.sep + name
                if os.path.isfile(full_path):
                    if (file_filter and file_filter(name)) or not file_filter:
                        fnode = FileNode(name, parent.local_path + os.sep + name, full_path, parent)
                        parent.append(fnode)
                elif os.path.isdir(full_path):
                    dirnode = DirNode(name, parent.local_path+os.sep + name, full_path, parent)
                    parent.append(dirnode)
                    new_dirs.append(dirnode)
        dirs = new_dirs

    return root


def find_first_file(dir_node):
    if len(dir_node.files) > 0:
        return dir_node.files[0]

    dirs = dir_node.folders
    while len(dirs) > 0:
        new_dirs = []
        for d in dirs:
            if len(d.files) > 0:
                return d.files[0]
            new_dirs.extend(d.folders)
        dirs = new_dirs
    return None
