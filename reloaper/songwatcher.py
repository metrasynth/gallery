import logging
from pathlib import Path

import attrs
from watchfiles import awatch, Change

from reloaper.pubsub import Key, hub

log = logging.getLogger(__name__)


@attrs.define
class SongWatcher:
    song_path: Path = attrs.field(converter=lambda p: p.resolve())

    async def watch(self):
        log.debug("Watching %r", self.song_path)
        log.debug("Initial change to kick off rendering.")
        self.publish_change()
        async for changes in awatch(self.song_path):
            for change, path in changes:
                if path != str(self.song_path):
                    continue
                if change != Change.modified:
                    continue
                self.publish_change()

    def publish_change(self):
        hub.publish(
            Key("song", "changed"),
            SongChanged(song_path=self.song_path),
        )


@attrs.define
class SongChanged:
    song_path: Path
