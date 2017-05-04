# messenger
from messenger import *

# logging
import logging
logger = logging.getLogger('systemwide')


def notify_success(build_id: str):
    try:
        CustomCallbackMessenger().send(
            status=200,
            id=build_id
        )
    except Exception as e:
        logger.error("Custom Notificatnion: " + e.__str__())


def notify_fail(build_id: str, error: str):
    try:
        CustomCallbackMessenger().send(
            status=500,
            id=build_id,
            error=error
        )
    except Exception as e:
        logger.error("Custom Notificatnion: " + e.__str__())