from django.shortcuts import render
from channels import Group
import json


def user_list(request):
    """
        Rendering localhost:8000/
    """
    return render(request, 'back/user_list.html')


def send_emittor_to_front(json):
    """
        To call when one cycle is over in the clustering algorithm
        Sends a new emittor to the frontend in the form of a JSON
    """
    Group('users').send({
        'text':json.dumps(json)
    })

def test(request):
    """
        Triggered whenever a user visits localhost:8000/test
        Will be called when lauching the simulation
    """
    send_emittor_to_front({'json':'containing data'})#TODO: use this function in the ML clustering algorithm
    Group('users').send({
        'text':json.dumps({
            'newelement': 'coucou'
        })
    })
    return render(request, 'back/user_list.html')
    

