

from git_repository import GitRepository
from core import Session



# repo = GitRepository("/home/wgryglas/Code/Python/pelicanReDoc")
# repo = GitRepository("/home/wgryglas/python/pelicanDoc")

# print repo.isModified()

# print repo.root_path


# session = Session(repo)
#
# print session._to_local_src_path_('/home/wgryglas/python/pelicanDoc/content/test.rst')

# session.set_active_file('test.rst')

# session.update_website()

# session.start_local_server()

#print session.get_sources_structure()


#root = session.get_sources_structure()

#local_images = session._env_.get_figures_folder_path_for('test.rst')

#print root.find_folder_by_path(session._env_.source_full_path(local_images))

# print repo.isRemoteUpToDate()

# from app_settings import AppSettings
# settings = AppSettings()
# # settings.set('figure_width', '500 px')
# # settings.saveToFile('/home/wgryglas/test_settings.xml')
# # settings.loadFromFile('/home/wgryglas/test_settings.xml')
#
# print settings.recent, settings.figure_width, settings.sort_images, settings.editor_font
#
# from app_settings import SystemSettings
#
# sys = SystemSettings()
#
# print sys.userSettingsDir, sys.settingsFilePath, sys.some_prop

# from file_templates import emptyFileTemplate
# print session.substituteTemplatText(emptyFileTemplate(), '/home/wgryglas/python/pelicanDoc/content/test.rst')


# import sys
# from pyqode.qt.QtCore import QRect
# from pyqode.qt.QtGui import QApplication
# from screenshot_selection import WindowRegionSelector
#
# def main():
#     app = QApplication(sys.argv)
#     ex = WindowRegionSelector(showRect=QRect(500, 300, 200, 200), hideOnClose=False)
#     ex.show()
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     main()