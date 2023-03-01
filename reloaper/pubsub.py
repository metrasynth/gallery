import logging

import aiopubsub
from aiopubsub import Key

log = logging.getLogger(__name__)

hub = aiopubsub.Hub()


def message_logger(key, message):
    log.debug("%r %r", key, message)
