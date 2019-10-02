from pyqode.qt.QtGui import QStandardItemModel, QStandardItem


def create_directory_tree_model(root_tree):
    node_mapping = dict()
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels([root_tree.name])

    root_item = model
    node_mapping[root_tree] = root_item

    for parent, files, dirs in root_tree.walk():
        parent_item = node_mapping[parent]
        for f in files:
            fitem = QStandardItem(f.name)
            fitem.setData(f)
            parent_item.appendRow(fitem)

        for d in dirs:
            ditem = QStandardItem(d.name)
            ditem.setData(d)
            node_mapping[d] = ditem
            parent_item.appendRow(ditem)

    return model
