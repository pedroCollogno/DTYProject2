from django.shortcuts import render
from channels import Group
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import FileForm
from django.core.files.storage import FileSystemStorage
import threading
import os


import data_process.main as main
import utils.station_utils as station_utils
import utils.loading as load


def user_list(request):
    """
        Rendering localhost:8000/
    """
    return render(request, 'back/user_list.html')


def send_emittor_to_front(json_obj):
    """
        To call when one cycle is over in the clustering algorithm
        Sends a new emittor to the frontend in the form of a JSON
    """
    Group('users').send({
        'text': json.dumps(json_obj)
    })


def test(request):
    """
        Triggered whenever a user visits localhost:8000/test
        Will be called when lauching the simulation
    """
    # TODO: use this function in the ML clustering algorithm
    send_emittor_to_front({'json': 'containing data'})
    Group('users').send({
        'text': json.dumps({
            'newelement': 'coucou'
        })
    })

    track_streams = []
    for path in paths:
        if path is not None:
            track_stream = load.get_track_stream_exs_from_prp(path)
            track_streams.append(track_stream)
    station_utils.sync_stations(*track_streams)

    t = threading.Thread(target=main.main, args=track_streams)
    t.start()
    return render(request, 'back/user_list.html')


@csrf_exempt  # makes a security exception for this function to be triggered
def upload(request):
    """
        Deals with the upload and save of a PRP file so that the user can upload his own scenario
        :return: success if the file is safe and sound
    """
    global paths
    if(request.method == 'POST'):
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage("scenarios/")
            paths = []
            for key in request.FILES.keys():
                global_file = request.FILES[key]
                filename = fs.save(global_file.name, global_file)
                paths.append(os.path.join(fs.location, filename))

        return(HttpResponse('<h1>Page was found</h1>'))
    else:
        return(HttpResponse('<h1>Page was not found</h1>'))
