# slack
import slackweb


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