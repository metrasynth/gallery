from rv.api import m
from sf.mmck import Group


# -----------------------------------------------------------------------------


def set_parameters(p, P):
    p.name = P.String('My Project', label='Project Name')
    p.voices = P.Integer(5, range=(3, 17), step=2)
    p.spread = P.Integer(5, range=(0, 128))


# -----------------------------------------------------------------------------


def build_project(p, c, project):
    project.name = p.name or ''
    
    multi = project.new_module(
        m.MultiSynth,
        random_phase=32768,
    )
    start = -(p.voices - 1) // 2
    end = start + p.voices
    generators = [
        project.new_module(
            m.AnalogGenerator,
            volume=256,
            polyphony_ch=16,
            waveform=m.AnalogGenerator.Waveform.saw,
            finetune=x * p.spread,
        )
        for x in range(start, end)
    ]
    multi >> generators >> project.output
    
    attack = m.MultiCtl.macro(project, *[(mod, 'attack') for mod in generators], name='attack')
    release = m.MultiCtl.macro(project, *[(mod, 'release') for mod in generators], name='release')
    sustain = m.MultiCtl.macro(project, *[(mod, 'sustain') for mod in generators], name='sustain')
    
    project.layout()
    
    c.random_phase = (multi, 'random_phase')
    c.attack = (attack, 'value')
    c.release = (release, 'value')
    c.sustain = (sustain, 'value')
    
    c.waveforms = Group()
    for i, module in enumerate(generators, 1):
        c.waveforms['generator_{}'.format(i)] = (module, 'waveform')
