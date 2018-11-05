from channels import Group
import json


def ws_connect(message):
    print('connected')
    Group('users').add(message.reply_channel)
    Group('users').send({
        'text':json.dumps({
            'newelement': 'caca'
        })
    })
    message.reply_channel.send({"accept": True})



def ws_disconnect(message):
    print('disconnected')
    Group('users').discard(message.reply_channel)
    message.reply_channel.send({"accept": True})

