

from git_repository import GitRepository
from core import Session

# repo = GitRepository("/home/wgryglas/Code/Python/pelicanReDoc")
# repo = GitRepository("/home/wgryglas/python/pelicanDoc")

# print repo.isModified()

# print repo.root_path


# session = Session(repo)

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


from os.path import dirname
print dirname("/home/wgryglas/python/pelicanDoc")