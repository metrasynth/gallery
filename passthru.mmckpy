import os

from rv.api import read_sunvox_file


# -----------------------------------------------------------------------------


def set_parameters(p, P):
    p.filename = P.String('', label='Filename')


def watch_paths(p):
    return [p.filename]


# -----------------------------------------------------------------------------


def build_project(p, c, project):
    if not os.path.exists(p.filename):
        print('{!r} does not exist'.format(p.filename))
        return

    meta = read_sunvox_file(p.filename).module
    project += meta
    meta >> project.output
