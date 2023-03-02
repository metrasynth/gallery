import asyncio
import ctypes
import logging
from datetime import datetime
from pathlib import Path

import attrs
import numpy as np

import sunvox.api
from reloaper.pubsub import hub, Key

log = logging.getLogger(__name__)


@attrs.define
class SongMapper:
    song_path: Path

    latest_map: np.ndarray | None = None
    latest_map_timestamp: datetime | None = None
    render_event: asyncio.Event = attrs.field(factory=asyncio.Event)

    def __attrs_post_init__(self):
        hub.add_subscriber(Key("song", "changed"), self.trigger_render)

    async def render_loop(self):
        log.debug("Starting SongMapper render loop")
        while True:
            await self.render_event.wait()
            self.render_event.clear()
            log.debug("Rendering song map...")
            with sunvox.api.Slot(self.song_path) as slot:
                song_length_lines = slot.get_song_length_lines()
                new_map = np.zeros(song_length_lines, np.uint32)
                get_time_map_result = slot.get_time_map(
                    start_line=0,
                    len=song_length_lines,
                    dest=new_map.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                    flags=sunvox.api.TIME_MAP.FRAMECNT,
                )
                log.debug("get_time_map_result %r", get_time_map_result)
                self.latest_map = new_map
                self.latest_map_timestamp = self.song_path.stat().st_mtime
                log.debug("latest_map[:5] %r", self.latest_map[:5])
                log.debug("latest_map_timestamp %r", self.latest_map_timestamp)

    def trigger_render(self, key, message):
        self.render_event.set()
