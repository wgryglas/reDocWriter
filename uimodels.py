from pyqode.qt.QtGui import QStandardItemModel, QStandardItem


def alwaysTrue(*args):
    return True


def create_directory_tree_model(root_tree, file_filter=alwaysTrue, folder_filter=alwaysTrue):

    model = QStandardItemModel()
    model.setHorizontalHeaderLabels([root_tree.name])

    mapping = {root_tree: model}

    for parent, files, dirs in root_tree.walk():
        if parent not in mapping:
            continue

        parent_item = mapping[parent]
        for f in filter(file_filter, files):
            fitem = QStandardItem(f.name)
            fitem.setData(f)
            parent_item.appendRow(fitem)

        for d in filter(folder_filter, dirs):
            ditem = QStandardItem(d.name)
            ditem.setData(d)
            mapping[d] = ditem
            parent_item.appendRow(ditem)

    return model



