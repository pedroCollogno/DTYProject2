from django.shortcuts import render
from channels import Group
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import FileForm
from django.core.files.storage import FileSystemStorage
import os

from ml_tools.threads import DataProcessThread
from ml_tools.utils import station_utils
from ml_tools.utils import loading as load
import logging
logger = logging.getLogger('backend')

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


def send_stations_positions(request):
    """
        To call to send station locations to frontend in the form of a JSON
    """
    track_streams = []
    if paths is not None:
        for path in paths:
            if path is not None:
                track_stream = load.get_track_streams_from_prp(path)
                track_streams.append(track_stream)
    json_obj = station_utils.get_station_coordinates(*track_streams)
    Group('users').send({
        'text': json.dumps(json_obj)
    })
    return(HttpResponse(json.dumps(json_obj), content_type="application/json"))


def initiate_emittors_positions(request):
    """
        To call to send station locations to frontend in the form of a JSON
    """
    track_streams = []
    if paths is not None:
        for path in paths:
            if path is not None:
                track_stream = load.get_track_streams_from_prp(path)
                track_streams.append(track_stream)
    station_utils.sync_stations(*track_streams)
    json_obj = station_utils.initiate_emittors_positions(*track_streams)
    Group('users').send({
        'text': json.dumps(json_obj)
    })
    return(HttpResponse(json.dumps(json_obj), content_type="application/json"))


def start_simulation(request):
    """
        Triggered whenever a user visits localhost:8000/test
        Will be called when lauching the simulation
    """
    send_emittor_to_front({'json': 'containing data'})
    Group('users').send({
        'text': json.dumps({
            'newelement': 'coucou'
        })
    })

    track_streams = []
    if paths is not None:
        for path in paths:
            if path is not None:
                track_stream = load.get_track_streams_from_prp(path)
                track_streams.append(track_stream)
    station_utils.sync_stations(*track_streams)

    global t
    t = DataProcessThread(*track_streams, debug=False)
    t.set_sender_function(send_emittor_to_front)
    t.start()
    return render(request, 'back/user_list.html')

@csrf_exempt  
def stop_simulation(request):
    logger.warning("AAAAAH")
    if t is not None:
        t.stop_thread()

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

        return(HttpResponse('POST ok !'))
    else:
        return(HttpResponse('POST failed'))
