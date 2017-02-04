from struct import pack

from rv.api import m, NOTE


# -----------------------------------------------------------------------------


def set_parameters(p, P):
    p.fn = P.String('(121 - x) / 120', label='Function', choices=[
        '.95 ** (x - 1)',
        '121 - x',
        'x',
        '(121 - x) / 120',
        '1 / x',
    ])


# -----------------------------------------------------------------------------


def build_project(p, c, project):
    values = [eval(p.fn) for x in range(1, 121)]
    print('\t'.join('{:02f}'.format(v) for v in values))
    sampler = project.new_module(
        m.Sampler,
        sample_interpolation='off',
        polyphony_ch=1,
    )
    sampler.volume_envelope.enable = False
    for x, value in enumerate(values):
        sample = sampler.Sample()
        sample.data = pack('<f', value)
        sample.loop_start = 0
        sample.loop_end = 1
        sample.finetune = 0
        sample.relative_note = 0
        sample.format = sampler.Format.float32
        sample.channels = sampler.Channels.mono
        sample.loop_type = sampler.LoopType.forward
        sampler.samples[x] = sample
        sampler.note_samples[NOTE(x + 1)] = x
    project.layout()
