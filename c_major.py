from s4ils import *

s = Session()

with s[INIT]:
    s.engine = c.Engine() | s
    s.fm = s.engine.new_module(rv.m.Fm) | s
    s.engine.output << s.fm | s
    s.track1 = s.engine.track(1)
    s.track2 = s.engine.track(2)
    s.track3 = s.engine.track(3)

with s[0, 0]:
    s.note1 = s.fm.note_on(n.C4) | s.track1 | s

with s[1, 0]:
    s.note2 = s.fm.note_on(n.E4) | s.track2 | s

with s[2, 0]:
    s.note3 = s.fm.note_on(n.G4) | s.track3 | s

with s[4, 0]:
    s.note1.off() | s
    s.note2.off() | s
    s.note3.off() | s

if __name__ == '__main__':
    play(s)
    input()
