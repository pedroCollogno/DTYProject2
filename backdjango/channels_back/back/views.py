from django.shortcuts import render
from channels import Group
import json



def user_list(request):
    return render(request, 'back/user_list.html')

def test(request):
    print('ok')
    Group('users').send({
        'text':json.dumps({
            'newelement': 'coucou'
        })
    })
    return render(request, 'back/user_list.html')
    
"""Triggered whenever a user visits localhost:8000/test"""