# slack
import slackweb

import requests as req

import redcap.settings as settings


class Messenger:
    """
    interface to messenger
    """
    def send(self, *args, **kwarg) -> str:
        """
        send message
        :param args:
        :param kwarg:
        :return:
        """
        raise NotImplementedError('not implemented')


class SlackMessenger(Messenger):
    """
    slack messenger
    """
    def __init__(self, sender: slackweb.Slack) -> None:
        self.sender = sender

    def send(self, *args, **kwargs) -> str:
        """
        send message
        :param args:
        :param kwargs:
        :return:
        """
        return self.sender.notify(**kwargs)


class CustomCallbackMessenger(Messenger):
    """
    custom messenger
    """
    def __init__(self) -> None:
        pass

    def send(self, *args, **kwargs) -> req.Response:
        """
        send message
        :param args:
        :param kwargs:
        :return:
        """
        try:
            return req.post(settings.CUSTOM_CALLBACK, json=kwargs)
        except NameError:
            pass