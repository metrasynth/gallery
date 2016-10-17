from s4ils import *


s = Session()

with s[INIT]:
    s.engine = s << c.Engine()
    s.track = s.engine.track(0)

with s[0, 0]:
    s.note = s << (s.track << c.NoteOn(n.C5))

with s[4, 0]:
    s << s.note.off()


if __name__ == '__main__':
    play(s)
