
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
        from os.path import getctime
        return


class DirNode(FileNode):
    def __init__(self, name, local_path, full_path, parent=None):
        FileNode.__init__(self, name, local_path, full_path, parent)
        self._children_ = []

    def __getitem__(self, item):
        return self._children_[item]

    def append(self, node):
        self._children_.append(node)

    def find_folder_by_path(self, full_path):
        if self.full_path == full_path:
            return self
        else:
            folder = self
            while folder:
                dirs = filter(lambda p: p.full_path in full_path, folder.folders)
                dirs.sort(key=lambda p: len(p.full_path))
                if len(dirs) > 0:
                    folder = dirs[0]
                    if folder.full_path == full_path:
                        return folder
                else:
                    folder = None
            return folder

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

    # def query(self, row, col):


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