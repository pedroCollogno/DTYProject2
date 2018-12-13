from channels import Group
import json
import logging
logger = logging.getLogger('backend')


def ws_connect(message):
    """
        Creates the websocket with parameters to be accepted by the browser
    """
    logger.debug('connected')
    Group('users').add(message.reply_channel)
    Group('users').send({
        'text': json.dumps({
            'newelement': 'hey'
        })
    })
    message.reply_channel.send({"accept": True})


def ws_disconnect(message):
    """
    Same but to trigger a certain action when a user disconnects
    """
    logger.debug('disconnected')
    Group('users').discard(message.reply_channel)
    message.reply_channel.send({"accept": True})
