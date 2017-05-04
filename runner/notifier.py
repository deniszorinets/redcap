from django.template.loader import render_to_string
from redcap.settings import SLACK_CHANNEL, SLACK_USERNAME

# messenger
from messenger import *
from redcap.slack import slack

# logging
import logging
logger = logging.getLogger('systemwide')


def notify_started(server_name: str, project_url: str, project_name: str):
    attachments = []
    attachment = {
        'title': 'Deploy',
        "color": '#3366CC',
        'text': render_to_string(
            'started_message.jinja',
            {'server': server_name, 'url': project_url, 'project': project_name}),
        'mrkdwn': True,
        'fields': [
            {'title': 'Project', 'value': project_url, 'short': True},
            {'title': 'Server', 'value': server_name, 'short': True}
        ],
        "mrkdwn_in": ["text", "pretext"]
    }
    attachments.append(attachment)
    try:
        return SlackMessenger(slack).send(
            text='Delivery started',
            channel=SLACK_CHANNEL,
            username=SLACK_USERNAME,
            icon_emoji=':sunny:',
            attachments=attachments)
    except NameError:
        pass
    except Exception as e:
        logger.error("Slack Notificatnion: " + e.__str__())

def notify_success(server_name: str, project_url: str, project_name: str):
    attachments = []
    attachment = {
        'title': 'Deploy',
        "color": 'good',
        'text': render_to_string(
            'success_message.jinja',
            {'server': server_name, 'url': project_url, 'project': project_name}),
        'mrkdwn': True,
        'fields': [
            {'title': 'Project', 'value': project_url, 'short': True},
            {'title': 'Server', 'value': server_name, 'short': True}
        ],
        "mrkdwn_in": ["text", "pretext"]
    }
    attachments.append(attachment)
    try:
        SlackMessenger(slack).send(
            text='Delivered',
            channel=SLACK_CHANNEL,
            username=SLACK_USERNAME,
            icon_emoji=':sunny:',
            attachments=attachments)
    except NameError:
        pass
    except Exception as e:
        logger.error("Slack Notificatnion: " + e.__str__())


def notify_fail(server_name: str, project_url: str, project_name: str, error: str):
    attachments = []
    attachment = {
        'title': 'Deploy',
        "color": 'danger',
        'text': render_to_string(
            'fail_message.jinja',
            {'server': server_name, 'url': project_url, 'project': project_name, 'error': error}),
        'mrkdwn': True,
        'fields': [
            {'title': 'Project', 'value': project_url, 'short': True},
            {'title': 'Server', 'value': server_name, 'short': True}
        ],
        "mrkdwn_in": ["text", "pretext"]
    }
    attachments.append(attachment)
    try:
        SlackMessenger(slack).send(
            text='Delivered',
            channel=SLACK_CHANNEL,
            username=SLACK_USERNAME,
            icon_emoji=':thunder_cloud_and_rain:',
            attachments=attachments)
    except NameError:
        pass
    except Exception as e:
        logger.error("Slack Notificatnion: " + e.__str__())