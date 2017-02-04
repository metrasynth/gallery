from rv.api import read_sunvox_file
from sails.api import module_clipboard_path


# -----------------------------------------------------------------------------


def set_parameters(p, P):
    pass


def watch_paths(p):
    return [module_clipboard_path()]


# -----------------------------------------------------------------------------


def build_project(p, c, project):
    meta = read_sunvox_file(module_clipboard_path()).module
    project += meta
    meta >> project.output
