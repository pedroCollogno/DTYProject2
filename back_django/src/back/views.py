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


class EWManager:

    def __init__(self):
        self.paths = []
        self.thread = DataProcessThread(debug=False)

    def add_path(self, path):
        self.paths.append(path)

    def clear_paths(self):
        self.paths = []

    def get_thread(self):
        return self.thread

    def get_paths(self):
        return self.paths


manager = EWManager()


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
    for path in manager.get_paths():
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
    for path in manager.get_paths():
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
    for path in manager.get_paths():
        if path is not None:
            track_stream = load.get_track_streams_from_prp(path)
            track_streams.append(track_stream)
    station_utils.sync_stations(*track_streams)

    manager.get_thread().set_track_streams(*track_streams)
    manager.get_thread().set_sender_function(send_emittor_to_front)
    manager.get_thread().start()
    return render(request, 'back/user_list.html')


@csrf_exempt
def stop_simulation(request):
    res = manager.get_thread().stop_thread()
    manager.clear_paths()
    if res:
        return (HttpResponse('Stopped thread !', status=200))
    return (HttpResponse('Could not stop...', status=500))


@csrf_exempt  # makes a security exception for this function to be triggered
def upload(request):
    """
        Deals with the upload and save of a PRP file so that the user can upload his own scenario
        :return: success if the file is safe and sound
    """
    if(request.method == 'POST'):
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage("scenarios/")
            manager.clear_paths()
            for key in request.FILES.keys():
                global_file = request.FILES[key]
                filename = fs.save(global_file.name, global_file)
                manager.add_path(os.path.join(fs.location, filename))

        return(HttpResponse('POST ok !'))
    else:
        return(HttpResponse('POST failed'))
