from django.shortcuts import render
from channels import Group
import json



def user_list(request):
    #clustering_bite() by Pierre à verrou
    return render(request, 'back/user_list.html')


def send_emittor_to_front(json):
    print('passed')
    Group('users').send({
        'text':json.dumps(json)
    })

def test(request):
    send_emittor_to_front({'json':'containing data'})
    Group('users').send({
        'text':json.dumps({
            'newelement': 'coucou'
        })
    })
    return render(request, 'back/user_list.html')
    
"""Triggered whenever a user visits localhost:8000/test"""
