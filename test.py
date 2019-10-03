


from core import GitRepository
from core import Session

repo = GitRepository("/home/wgryglas/Code/Python/pelicanReDoc")


print repo.isModified()

# print repo.root_path


session = Session(repo.root_path)


session.update_website()
# session.update_website()

# session.start_local_server()

print session.get_sources_structure()
