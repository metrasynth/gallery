"""
From Phil Dick's "Do Androids Dream of Electric Sheep?"

JR - Kipple is useless objects, like junk mail or match folders after you use
the last match or gum wrappers of yesterday's homeopape. When nobody's around,
kipple reproduces itself. For instance, if you go to bed leaving any kipple
around your apartment, when you wake up the next morning there's twice as
much of it. It always gets more and more.

Pris- I see.

JR - There's the First Law of Kipple, "Kipple drives out nonkipple."
Like Gresham's law about bad money. And in these apartments there's been
nobody there to fight the kipple.

Pris - So it has taken over completely. Now I understand.

JR - Your place, here, this apartment you've picked - it's too kipple-ized
to live in. We can roll the kipple-factor back; we can do like I said,
raid the other apartments. But -

Pris - But what?

JR - We can't win.

Pris - Why not?

JR - No one can win against kipple, except temporarily and maybe in one spot,
like in my apartment I've sort of created a stasis between the pressure of
kipple and nonkipple, for the time being. But eventually I'll die or go away,
and then the kipple will again take over. It's a universal principle operating
throughout the universe; the entire universe is moving toward a final state of
total, absolute kippleization.
"""
from random import Random

from rv.api import m
from rv.controller import DependentRange, Range


# -----------------------------------------------------------------------------


def set_parameters(p, P):
    # Define your parameters below by adding to the
    # `p` object.
    #
    # You can define P.String or P.Integer parameters.
    #
    # Example:
    #
    #   p.name = P.String(label='Project Name')
    #   p.voices = P.Integer(5, range=(3, 17), step=2)
    #   p.spread = P.Integer(5, range=(0, 128))

    def probability():
        return P.Integer(50, range=(0, 100))

    p.name = P.String(label='Project Name')
    p.random_seed = P.Integer(0, range=(0, 2**30))
    p.module_count_min = P.Integer(1, range=(1, 200))
    p.module_count_max = P.Integer(20, range=(1, 200))
    p.max_bifurcations = P.Integer(4, range=(2, 10))
    p.max_cycles = P.Integer(10000, range=(1000, 100000))

    p.p_bifurcations = probability()
    p.p_terminations = probability()
    p.p_reunions = probability()
    p.p_reunion_amp = probability()

    p.p_synths = probability()
    p.p_effects = probability()

    p.p_analog_gen = probability()
    p.p_drumsynth = probability()
    p.p_fm = probability()
    p.p_generator = probability()
    p.p_kicker = probability()
    p.p_spectravoice = probability()

    p.p_amplifier = probability()
    p.p_compressor = probability()
    p.p_dc_blocker = probability()
    p.p_delay = probability()
    p.p_distortion = probability()
    p.p_echo = probability()
    p.p_eq = probability()
    p.p_filter = probability()
    p.p_filter_pro = probability()
    p.p_lfo = probability()
    p.p_loop = probability()
    p.p_modulator = probability()
    p.p_pitch_shifter = probability()
    p.p_reverb = probability()
    p.p_vibrato = probability()
    p.p_vocal_filter = probability()
    p.p_waveshaper = probability()

    p.p_feedback = probability()
    p.p_glide = probability()
    p.p_multisynth = probability()
    p.p_pitch2ctl = probability()
    p.p_sound2ctl = probability()
    p.p_velocity2ctl = probability()


# -----------------------------------------------------------------------------


def build_project(p, c, project):

    def printed(*args):
        label, x = args if len(args) == 2 else ('--', args[0])
        print(label, x)
        return x

    project.name = p.name or '{}-synth'.format(p.random_seed)

    MAX = 2**30
    rmaster = Random(p.random_seed)
    new_seed = lambda: rmaster.randint(0, MAX)
    new_random = lambda: Random(new_seed())
    mrandom = new_random()  # mutations
    nrandom = new_random()  # names
    trandom = new_random()  # tracks

    mutations = []

    class Track:
        def __init__(self, *mods, ancestor=None):
            self.random = new_random()
            self.finished = False
            self.ancestor = ancestor
            self.mods = list(mods)

        def __lshift__(self, other):
            self.mods.append(other)
            if len(self.mods) == 1 and self.ancestor:
                self.ancestor.tail << self.tail
                self.ancestor.finish()

        @property
        def previous(self):
            for mod in reversed(self.mods[:-1]):
                yield mod
            if self.ancestor:
                for mod in self.ancestor.previous:
                    yield mod

        @property
        def tail(self):
            if self.mods:
                return self.mods[-1]
            elif self.ancestor:
                return self.ancestor.tail

        @property
        def behaviors(self):
            return getattr(self.tail, 'behaviors', set())

        @property
        def supported_mutations(self):
            return set(self._supported_mutations())
        def _supported_mutations(self):
            if m.Behavior.sends_audio in self.behaviors:
                yield 'effect'
                if not self.finished:
                    yield 'reunion'
            if m.Behavior.sends_notes in self.behaviors:
                yield 'synth'
            if not self.finished:
                yield 'bifurcation'
                yield 'termination'

        def finish(self):
            self.finished = True
            print('{:x}.finished'.format(id(self)))

    multisynth = project.new_module(m.MultiSynth)
    tracks = [
        Track(multisynth),
    ]

    def randomize_controllers(mod, random, skip=set()):
        choices = sorted(list(set(mod.controllers) - skip))
        for ctlname, ctl in mod.controllers.items():
            if not ctl.attached(mod):
                choices.remove(ctlname)
        print('------------', choices)
        count = random.randint(0, len(choices))
        for _ in range(count):
            ctl_name = random.choice(choices)
            choices.remove(ctl_name)
            ctl = mod.controllers[ctl_name]
            t = ctl.value_type
            if isinstance(t, DependentRange):
                t = t.parent(mod)
            if isinstance(t, Range):
                value = random.randint(t.min, t.max)
            elif t is bool:
                value = random.choice([True, False])
            else:
                print(t)
                value = random.choice(list(t))
            print('setting {}.{} to {}'.format(mod, ctl_name, value))
            setattr(mod, ctl_name, value)

    mutation_types = ['synth', 'effect', 'bifurcation', 'termination', 'reunion']

    def generate_controllers():
        names1 = ['pen', 'tao', 'uber', 'angul', 'baron', 'zarg', 'yes', 'no', 'hero', 'oct', 'touch', 'scene', 'arp', 'chord', 'scale', 'sus', 'garn', 'con', 'eff', 'sync', 'super', 'meta']
        names2 = ['ultimate', 'ish', 'istic', 'tronic', 'ating', 'onomous', 'alpha', 'betron', 'thespa', 'ave', 'scale', 'scene', 'pad', 'trol', 'fect', 'sync']
        names3 = ['zes', 'transmob', 'farn', 'garb', 'sonos', 'chronos', 'mab', 'sort', 'port', 'part', 'suss', 'pitch', 'shift', 'easy', 'master', 'zono', 'ren', 'part', 'hyper', 'sub']
        names4 = ['ticulator', 'ulator', 'system', 'ule', 'ran', 'icle', 'ishment', 'erator', 'stin', 'tain', 'mod', 'tap', 'guide', 'master', 'plasty', 'ticular']
        structures = [
            [names1, names2, '_', names3, names4],
            [names1, names4, '_', names3, names2],
            [names3, names4, '_', names1, names2],
            [names3, names2, '_', names1, names4],
            [names1, '_', names1, names2],
            [names1, '_', names1, names4],
            [names1, '_', names3, names2],
            [names1, '_', names3, names4],
            [names3, '_', names1, names2],
            [names3, '_', names1, names4],
            [names3, '_', names3, names2],
            [names3, '_', names3, names4],
            [names1, names2, '_', names1],
            [names1, names4, '_', names1],
            [names3, names2, '_', names1],
            [names3, names4, '_', names1],
            [names1, names2, '_', names3],
            [names1, names4, '_', names3],
            [names3, names2, '_', names3],
            [names3, names4, '_', names3],
            [names1, names2],
            [names3, names4],
            [names1, names4],
            [names3, names2],
        ]
        used_names = set()
        def gen_name():
            structure = nrandom.choice(structures)
            while True:
                name = ''.join(part if isinstance(part, str) else nrandom.choice(part) for part in structure)
                if name not in used_names:
                    used_names.add(name)
                    return name
        all_ctls = []
        for module in project.modules[1:]:
            for ctlname, ctl in module.controllers.items():
                if ctl.attached(module):
                    all_ctls.append((module, ctlname))
                else:
                    print('skipping', module, ctlname)
        nrandom.shuffle(all_ctls)
        for groupnum in range(8):
            groupname = gen_name()
            for ctlnum in range(8):
                if all_ctls:
                    label = gen_name()
                    mod, ctlname = all_ctls.pop()
                    c[groupname][label] = (mod, ctlname)

    def go():
        module_count = printed(rmaster.randint(p.module_count_min, p.module_count_max))
        loops = 0
        last_mod_count = len(project.modules) - 2
        while last_mod_count < module_count:
            current_mod_count = len(project.modules) - 2
            if last_mod_count == current_mod_count:
                loops += 1
                if loops > p.max_cycles:
                    raise RuntimeError('Exhausted!')
            else:
                loops = 0
                last_mod_count = current_mod_count
            mutation_type = mrandom.choice(mutation_types)
            prob_name = 'p_{}s'.format(mutation_type)
            if mrandom.randint(1, 100) <= p[prob_name]:
                fn = mrandom.choice([m for m in mutations if m.behavior == mutation_type])
                if mrandom.randint(1, 100) <= fn.probability:
                    compatible_tracks = [t for t in tracks if mutation_type in t.supported_mutations]
                    if compatible_tracks:
                        track = mrandom.choice(compatible_tracks)
                        print('mutation={} track:{:x}'.format(fn.__name__, id(track)))
                        fn(track)
        # dc_blocker = project.new_module(m.DcBlocker)
        # final_amp = project.new_module(m.Amplifier)
        open_audio_tracks = [t for t in tracks if 'effect' in t.supported_mutations]
        # project.output << dc_blocker << final_amp << [t.tail for t in open_audio_tracks]
        project.output << [t.tail for t in open_audio_tracks]
        project.layout()
        # print(project.module_connections)
        print(project.modules)
        generate_controllers()

    # ----

    def mutation(behavior, probability):
        def decorator(fn):
            fn.behavior = behavior
            fn.probability = probability
            mutations.append(fn)
            return fn
        return decorator

    def generic_random_mod(track, cls, skip=set()):
        mod = project.new_module(cls)
        randomize_controllers(mod, track.random, skip)
        track.tail >> mod
        track << mod
        return mod

    @mutation('synth', p.p_analog_gen)
    def analog_gen(track):
        # TODO: waveform generation
        generic_random_mod(track, m.AnalogGenerator)

    @mutation('synth', p.p_drumsynth)
    def drumsynth(track):
        generic_random_mod(track, m.DrumSynth)

    @mutation('synth', p.p_fm)
    def fm(track):
        generic_random_mod(track, m.Fm)

    @mutation('synth', p.p_generator)
    def generator(track):
        # TODO: waveform generation
        generic_random_mod(track, m.Generator)

    @mutation('synth', p.p_kicker)
    def kicker(track):
        generic_random_mod(track, m.Kicker)

    @mutation('synth', p.p_spectravoice)
    def spectravoice(track):
        mod = generic_random_mod(track, m.SpectraVoice)
        count = track.random.randint(1, len(mod.harmonics))
        for harmonic in mod.harmonics[:count]:
            harmonic.freq_hz = track.random.randint(0, 22050)
            harmonic.volume = track.random.randint(0, 255)
            harmonic.width = track.random.randint(0, 3)
            harmonic.type = track.random.choice(list(m.SpectraVoice.HarmonicType))

    @mutation('effect', p.p_amplifier)
    def amplifier(track):
        generic_random_mod(track, m.Amplifier, {'dc_offset', 'gain'})

    @mutation('effect', p.p_compressor)
    def compressor(track):
        generic_random_mod(track, m.Compressor)

    @mutation('effect', p.p_dc_blocker)
    def dc_blocker(track):
        generic_random_mod(track, m.DcBlocker)

    @mutation('effect', p.p_delay)
    def delay(track):
        generic_random_mod(track, m.Delay)

    @mutation('effect', p.p_distortion)
    def distortion(track):
        generic_random_mod(track, m.Distortion)

    @mutation('effect', p.p_echo)
    def echo(track):
        generic_random_mod(track, m.Echo)

    @mutation('effect', p.p_eq)
    def eq(track):
        generic_random_mod(track, m.Eq)

    @mutation('effect', p.p_filter)
    def filter_(track):
        generic_random_mod(track, m.Filter)

    @mutation('effect', p.p_filter_pro)
    def filter_pro(track):
        generic_random_mod(track, m.FilterPro)

    @mutation('effect', p.p_lfo)
    def lfo(track):
        generic_random_mod(track, m.Lfo)

    @mutation('effect', p.p_loop)
    def loop(track):
        generic_random_mod(track, m.Loop)

    @mutation('effect', p.p_pitch_shifter)
    def pitch_shifter(track):
        generic_random_mod(track, m.PitchShifter)

    @mutation('effect', p.p_reverb)
    def reverb(track):
        generic_random_mod(track, m.Reverb)

    @mutation('effect', p.p_vibrato)
    def vibrato(track):
        generic_random_mod(track, m.Vibrato)

    @mutation('effect', p.p_vocal_filter)
    def vocal_filter(track):
        generic_random_mod(track, m.VocalFilter)

    @mutation('effect', p.p_waveshaper)
    def waveshaper(track):
        # TODO: waveform generation
        generic_random_mod(track, m.WaveShaper)

    @mutation('effect', p.p_feedback)
    def feedback(track):
        ancestors = list(track.previous)
        if ancestors:
            dest = track.random.choice(ancestors)
            fb1 = project.new_module(m.Feedback)
            fb2 = project.new_module(m.Feedback)
            randomize_controllers(fb1, track.random)
            randomize_controllers(fb2, track.random)
            track.tail >> fb1 >> fb2 >> dest

    @mutation('synth', p.p_glide)
    def glide(track):
        generic_random_mod(track, m.Glide)

    @mutation('synth', p.p_multisynth)
    def multisynth(track):
        generic_random_mod(track, m.MultiSynth)

    @mutation('synth', p.p_pitch2ctl)
    def pitch2ctl(track):
        # TODO
        pass

    @mutation('effect', p.p_sound2ctl)
    def sound2ctl(track):
        # TODO
        pass

    @mutation('synth', p.p_velocity2ctl)
    def velocity2ctl(track):
        # TODO
        pass

    @mutation('termination', p.p_terminations)
    def maybe_terminate(track):
        track.finish()

    @mutation('bifurcation', p.p_bifurcations)
    def maybe_bifurcate(track):
        bifurcations = track.random.randint(2, p.max_bifurcations)
        for _ in range(2, bifurcations + 1):
            tracks.append(Track(ancestor=track))

    @mutation('reunion', p.p_reunion_amp)
    def reunion_amp(track):
        compatible_tracks = [t for t in tracks if 'reunion' in t.supported_mutations and t is not track]
        if compatible_tracks:
            track2 = track.random.choice(compatible_tracks)
            print(' + track2:{:x}'.format(id(track2)))
            mod = generic_random_mod(track, m.Amplifier, {'dc_offset'})
            track2.tail >> mod

    @mutation('reunion', p.p_modulator)
    def modulator(track):
        compatible_tracks = [t for t in tracks if 'reunion' in t.supported_mutations and t is not track]
        if compatible_tracks:
            modulator = track.random.choice(compatible_tracks)
            print(' + modulator:{:x}'.format(id(modulator)))
            mod = generic_random_mod(track, m.Modulator)
            modulator.tail >> mod

    # ----

    go()
    print('Going... going... gone!')
