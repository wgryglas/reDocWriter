
# Define linter after loading role names so that restructuredtext_linter will see custom roles
# Can't be done in external file to make it work for using native pyqode.rst toolset because
# backend server makes own instance of loaded modules and thus
# docutils_customization.register_role_names()
# must be called here instead main app file

import restructuredtext_lint
import docutils_customization
docutils_customization.register_role_names()

ERRORS_LEVELS = {
    'INFO': 0,
    'WARNING': 1,
    'ERROR': 2,
    'SEVERE': 2
}


def linter(request_data):
    code = request_data['code']
    ret_val = []
    for err in sorted(restructuredtext_lint.lint(code), key=lambda x: x.line):
        ret_val.append((err.message, ERRORS_LEVELS[err.type], err.line - 1))
    return ret_val
