from rv.api import m, Pattern, Note, Project
from sf.mmck import Group


# -----------------------------------------------------------------------------


def set_parameters(p, P):
    p.name = P.String('Fingerdrum', label='Project Name')
    p.left_drums = P.String('BD01 BD51 SD12', label='Left Finger Drums')
    p.right_drums = P.String('HH01 HH12 HH23 HH41 HH52', label='Right Finger Drums')
    p.left_sequence = P.String('x..x..x..x.x.xx.', label='Left Finger Sequence')
    p.right_sequence = P.String('xxx.x.xxx.x.xxx.', label='Right Finger Sequence')
    p.loops = P.Integer(8, label='Loops')


# -----------------------------------------------------------------------------


def generate_hand(drums, sequence, lines, track, module):
    drums = [getattr(m.DrumSynth.DRUMNOTE, name) for name in drums.split()]
    def gen(pat, new):
        finger = -1
        for line in range(lines):
            if sequence[line % len(sequence)] == 'x':
                finger = (finger + 1) % len(drums)
                drum = drums[finger]
                yield line, track, Note(note=drum, vel=129, module=module.index + 1)
    return gen


def build_project(p, c, project):
    assert len(p.left_sequence) == len(p.right_sequence)

    note_in = project.new_module(m.MultiSynth, name='note in')

    drums = Project()
    drums.name = 'Drums'
    drumsmeta = project.new_module(m.MetaModule, project=drums, input_module=254)
    drumsmeta.play_patterns = True
    note_in >> drumsmeta >> project.output

    drumsmod = drums.new_module(m.DrumSynth)
    drumsmod >> drums.output

    lines = len(p.left_sequence) * p.loops
    drumspat = Pattern(tracks=2, lines=lines)
    drums += drumspat
    drumspat.set_via_gen(generate_hand(p.left_drums, p.left_sequence, lines, 0, drumsmod))
    drumspat.set_via_gen(generate_hand(p.right_drums, p.right_sequence, lines, 1, drumsmod))

    project.name = p.name

    c.common = Group()
    c.common.bpm = (drumsmeta, 'bpm')
    c.common.tpl = (drumsmeta, 'tpl')
