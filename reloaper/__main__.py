import asyncio
import logging
from pathlib import Path

import typer
from rich.logging import RichHandler

from reloaper.pubsub import hub, Key, message_logger
from reloaper.songwatcher import SongWatcher

log = logging.getLogger(__name__)


def entrypoint(song_path: Path):
    init_logging()
    init_hub_logging()
    asyncio.run(main(song_path))


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


async def main(song_path: Path):
    song_watcher = SongWatcher(song_path=song_path)
    task = song_watcher.watch()
    await task


if __name__ == "__main__":
    typer.run(entrypoint)
