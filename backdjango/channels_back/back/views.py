from django.shortcuts import render
from channels import Group
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import FileForm
from django.core.files.storage import FileSystemStorage




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


@csrf_exempt#makes a security exception for this function to be triggered
def upload(request):
    """
        Deals with the upload and save of a PRP file so that the user can upload his own scenario
        :return: success if the file is safe and sound
    """
    global path
    if(request.method=='POST'):
        form=FileForm(request.POST, request.FILES)
        if form.is_valid():
            global_file=request.FILES['File']
            fs=FileSystemStorage()
            filename=fs.save(global_file.name,global_file)
            path=fs.location+'/'+filename
        return(HttpResponse('<h1>Page was found</h1>'))
    else:
        return(HttpResponse('<h1>Page was not found</h1>'))


