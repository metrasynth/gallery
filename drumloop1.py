from s4ils import *


@c.Generator.factory
def bassdrummer(track):
    def kick():
        cursor.s.drums.on(n.C4) | track | cursor
    cursor = first_cursor = yield
    while True:
        beat, tick = cursor - first_cursor
        if tick == 0:
            kick()
        if tick == 12 and beat % 16 == 15:
            kick()
        cursor = yield


@c.Generator.factory
def snaredrummer(track):
    def smack():
        cursor.s.drums.on(n.G5) | track | cursor
    cursor = first_cursor = yield
    while True:
        beat, tick = cursor - first_cursor
        if tick == 0 and beat % 4 % 2 == 1:
            smack()
        cursor = yield


@c.Generator.factory
def asciidrummer(tracks, patterns, note_map, ticks_per_step=6, singleshot=False):
    cursor = first_cursor = yield
    finished = 0
    if not isinstance(tracks, list):
        tracks = [tracks]
        patterns = [patterns]
    while cursor:
        beat, tick = cursor - first_cursor
        ticks = beat * 24 + tick
        if ticks % ticks_per_step == 0:
            for track, pattern in zip(tracks, patterns):
                p_len = len(pattern)
                loops = ticks // ticks_per_step // p_len
                pos = ticks // ticks_per_step % p_len
                if not singleshot or loops == 0:
                    char = pattern[pos]
                    if char == '.':
                        track.off() | cursor
                    elif char in note_map:
                        module, note = note_map[char]
                        module.on(note) | track | cursor
                elif singleshot and loops > 0 and pos == 0:
                    finished += 1
        if not singleshot or finished < len(patterns):
            cursor = yield
        else:
            cursor = None


s = Session()

with s[INIT]:
    s.engine = c.Engine() | s
    s.track = s.engine.track
    s.drums = s.engine.new_module(rv.m.DrumSynth) | s
    s.engine.output << s.drums | s

with s[0, 0]:
    s.bass = bassdrummer(s.track(1)) | s

with s[14, 0]:
    s.snare = snaredrummer(s.track(2)) | s

with s[0, 0]:
    s.drummer = asciidrummer(
        s.track(3),
        'cccc' * 15 + 'cco-',
        {
            'c': (s.drums, n.A6),
            'o': (s.drums, n.A5),
        }
    ) | s


if __name__ == '__main__':
    play(s, forever=True)
    input()
