
def dummy_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    from docutils.nodes import Text
    return [Text("")], []


custom_roles = ['vector', 'lorem', 'input', 'number']


def register_role_names(*args):
    """
    Registers roles names in docutils so that error checker will not
    assume those exists. The list of roles should match roles used under
    project that is being used for RST compilation
    :param args:
    :return:
    """
    from docutils.parsers.rst import roles
    from itertools import chain

    for role_name in chain(custom_roles, args):
        roles.register_local_role(role_name, dummy_role)

