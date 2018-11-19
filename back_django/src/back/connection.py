from channels import Group
import json


def ws_connect(message):
    """
        Creates the websocket with parameters to be accepted by the browser
    """
    print('connected')
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
    print('disconnected')
    Group('users').discard(message.reply_channel)
    message.reply_channel.send({"accept": True})
