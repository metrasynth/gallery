import begin
from s4ils import *

from drumloop1 import bassdrummer, snaredrummer, asciidrummer


def sunsynth(name):
    return rv.read_sunvox_file(
        '../sunvox/instruments/{}.sunsynth'.format(name)).module


@c.Generator.factory
def drummers(kickstart, smackstart, artstart):
    cursor = yield
    s = cursor.s
    s.kicker = bassdrummer(s.track(1)) | s + (kickstart, 0)
    s.smacker = snaredrummer(s.track(2)) | s + (smackstart, 0)
    s.artsy = asciidrummer(
        s.track(3),
        'cccc' * 15 + 'cco-',
        {
            'c': (s.drums, n.A6),
            'o': (s.drums, n.A5)
        }
    ) | cursor + (artstart, 0)


@c.Generator.factory
def bassist():
    cursor = yield
    s = cursor.s
    s.boomda = asciidrummer(
        [s.track(4), s.track(5)],
        [
            '--x--x--bbb-v-vc' '-xx-x--x-bb-v-cx',

            '----------------' '----------------'
            '----------------' '---------BB-V-CX',
        ],
        {
            'x': (s.bass, n.D2),
            'c': (s.bass, n.E2),
            'v': (s.bass, n.F2),
            'b': (s.bass, n.G2),
            'X': (s.bass2, n.D2 + 7 + 12),
            'C': (s.bass2, n.E2 + 7 + 12),
            'V': (s.bass2, n.F2 + 7 + 12),
            'B': (s.bass2, n.G2 + 7 + 12),
        },
    ) | cursor


@c.Generator.factory
def floomster(octave):
    cursor = yield
    s = cursor.s
    s.flown = asciidrummer(
        [s.track(6)],
        [
            '12345--4321-----.',
        ],
        {
            '1': (s.floom, n.D3 + octave * 12),
            '2': (s.floom, n.D4 + octave * 12),
            '3': (s.floom, n.G4 + octave * 12),
            '4': (s.floom, n.C5 + octave * 12),
            '5': (s.floom, n.D5 + octave * 12),
        },
        ticks_per_step=2,
        singleshot=True,
    ) | s


s = Session()

with s[INIT]:
    s.engine = c.Engine() | s
    s.track = s.engine.track
    s.drums = s.engine.new_module(rv.m.DrumSynth) | s
    s.bass = s.engine.new_module(sunsynth('bass/analog_bass')) | s
    s.bass2 = s.engine.new_module(sunsynth('bass/analog_bass2')) | s
    s.floom = s.engine.new_module(sunsynth('keyboard/SuperSynth')) | s
    s.engine.output << s.drums | s
    s.engine.output << s.bass | s
    s.engine.output << s.bass2 | s
    s.engine.output << s.floom | s

with s[0, 0]:
    s.drummers = drummers(0, 14, 16) | s
    s.bassist = bassist() | s

with s[32, 3]:
    floomster(0) | s

with s[48, 3]:
    floomster(1) | s

with s[64, 3]:
    floomster(0) | s


@begin.start
@begin.logging
def main():
    play_sunvosc(s, bpm=115, forever=True)
