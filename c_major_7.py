from s4ils import *

s = Session()

with s[INIT]:
    s.engine = c.Engine() | s
    s.fm = s.engine.new_module(rv.m.Fm) | s
    s.engine.output << s.fm | s
    s.track1 = s.engine.track(1)
    s.track2 = s.engine.track(2)
    s.halfnote = (2, 0)

with s[0, 0]:
    note = s.fm.note_on(n.C4, 10) | s.track1 | s
    note.off() | s + s.halfnote

with s[0, 6]:
    (s.fm.note_on(n.E4, 20) | s.track2 | s).off() | s + (4, 0)

with s[0, 12]:
    for offset, note in enumerate([n.G4, n.B4, n.C5, n.E5, n.G5, n.B5, n.C6, n.E6, n.G6, n.B6]):
        track = s.engine.track(3 + offset)
        start = offset * 6
        vel = (5 + offset) * 6
        (s.fm.note_on(note, vel) | track | s + start).off() | s + start + s.halfnote

if __name__ == '__main__':
    play(s)
    input()
