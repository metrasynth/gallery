import asyncio
import logging
from pathlib import Path

import typer
from rich.logging import RichHandler

import sunvox.api
from reloaper.pubsub import hub, Key, message_logger
from reloaper.songmapper import SongMapper
from reloaper.songrenderer import SongRenderer
from reloaper.songwatcher import SongWatcher

log = logging.getLogger(__name__)


def entrypoint(song_path: Path, freq: int = 44100):
    song_path = song_path.resolve()
    init_logging()
    init_sunvox(freq=freq)
    init_hub_logging()
    asyncio.run(main(song_path=song_path))


def init_hub_logging():
    hub.add_subscriber(Key("*"), message_logger)


def init_logging():
    FORMAT = "%(message)s"
    logging.basicConfig(
        level=logging.NOTSET,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    log.debug("Logging initialized")


def init_sunvox(*, freq: int):
    flags = sunvox.api.INIT_FLAG.USER_AUDIO_CALLBACK | sunvox.api.INIT_FLAG.ONE_THREAD
    sunvox.api.init(None, freq, 2, flags)
    log.debug("Initialized SunVox library")


async def main(*, song_path: Path):
    song_watcher = SongWatcher(song_path=song_path)
    song_mapper = SongMapper(song_path=song_path)
    song_renderer = SongRenderer(song_path=song_path)
    await asyncio.gather(
        song_watcher.watch(),
        song_mapper.render_loop(),
        song_renderer.render_loop(),
    )


if __name__ == "__main__":
    typer.run(entrypoint)
