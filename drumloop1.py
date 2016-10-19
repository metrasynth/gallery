from s4ils import *


@c.Generator.factory
def bassdrummer(track):
    def kick():
        cursor.drums.on(n.C5) | track | cursor
    while True:
        cursor = yield
        if cursor.tick == 0:
            kick()
        if cursor.tick == 12 and cursor.beat % 16 == 15:
            kick()


@c.Generator.factory
def snaredrummer(track):
    def smack():
        cursor.drums.on(n.G5) | track | cursor
    while True:
        cursor = yield
        if cursor.tick == 0 and cursor.beat % 4 % 2 == 1:
            smack()


@c.Generator.factory
def asciidrummer(track, pattern, note_map, ticks_per_step=6):
    while True:
        cursor = yield
        if cursor.tick % ticks_per_step == 0:
            pos = cursor.ticks // ticks_per_step % len(pattern)
            char = pattern[pos]
            if char in note_map:
                module, note = note_map[char]
                module.on(note) | track | cursor


s = Session()

with s[INIT]:
    s.engine = c.Engine() | s
    s.track = s.engine.track
    s.drums = s.engine.new_module(rv.m.DrumSynth) | s
    s.engine.output << s.drums | s

with s[0, 0]:
    s.bass = bassdrummer(s.track(1)) | s

with s[15, 0]:
    s.snare = snaredrummer(s.track(2)) | s

with s[16, 0]:
    s.drummer = asciidrummer(
        s.track(3),
        'c-c-' * 15 + 'cco-',
        {
            'c': (s.drums, n.A6),
            'o': (s.drums, n.A5),
        }
    ) | s


if __name__ == '__main__':
    play(s, forever=True)
    input()
