from channels import Group
import json

"""Creates the websocket with parameters to be accepted by the browser"""
def ws_connect(message):
    print('connected')
    Group('users').add(message.reply_channel)
    Group('users').send({
        'text':json.dumps({
            'newelement': 'hey'
        })
    })
    message.reply_channel.send({"accept": True})

"""Same but to trigger a certain action when a user disconnects"""

def ws_disconnect(message):
    print('disconnected')
    Group('users').discard(message.reply_channel)
    message.reply_channel.send({"accept": True})

