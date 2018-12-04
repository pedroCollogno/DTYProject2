import os
import json
import shutil
import logging
logger = logging.getLogger('backend')

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from channels import Group

from ml_tools.utils import station_utils
from ml_tools.utils import loading as load
from .forms import FileForm
from .ewmanager import EWManager
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
    track_streams = manager.get_track_streams()

    json_obj = station_utils.get_station_coordinates(*track_streams)
    Group('users').send({
        'text': json.dumps(json_obj)
    })
    return(HttpResponse(json.dumps(json_obj), content_type="application/json"))


def initiate_emittors_positions(request):
    """
        To call to send station locations to frontend in the form of a JSON
    """
    track_streams = manager.get_track_streams()

    json_obj = station_utils.initiate_emittors_positions(*track_streams)
    Group('users').send({
        'text': json.dumps(json_obj)
    })
    return(HttpResponse(json.dumps(json_obj), content_type="application/json"))


def start_simulation(request):
    """
        Called when lauching the simulation
    """
    send_emittor_to_front({'json': 'containing data'})
    Group('users').send({
        'text': json.dumps({
            'simulation': 'start using DB_SCAN, corrected by Deep Learning for clustering'
        })
    })
    manager.reset_thread()

    track_streams = manager.get_track_streams()
    manager.set_deep(False)
    manager.set_mix(True)
    manager.get_thread().set_track_streams(*track_streams)
    manager.get_thread().set_sender_function(send_emittor_to_front)
    manager.get_thread().start()
    return render(request, 'back/user_list.html')


def start_simulation_ml(request):
    """
        Called when lauching the simulation using only db_scan algorithm for clustering
    """
    send_emittor_to_front({'json': 'containing data'})
    Group('users').send({
        'text': json.dumps({
            'simulation': 'start using only DB_SCAN clustering'
        })
    })
    manager.reset_thread()

    track_streams = manager.get_track_streams()
    manager.set_deep(False)
    manager.set_mix(False)
    manager.get_thread().set_track_streams(*track_streams)
    manager.get_thread().set_sender_function(send_emittor_to_front)
    manager.get_thread().start()
    return render(request, 'back/user_list.html')


def start_simulation_dl(request):
    """
        Called when lauching the simulation using only deep learning for clustering
    """

    send_emittor_to_front({'json': 'containing data'})
    Group('users').send({
        'text': json.dumps({
            'simulation': 'start using only Deep Learning for clustering'
        })
    })
    manager.reset_thread()

    track_streams = manager.get_track_streams()
    manager.set_deep(True)
    manager.set_mix(False)
    manager.get_thread().set_track_streams(*track_streams)
    manager.get_thread().set_sender_function(send_emittor_to_front)
    manager.get_thread().start()
    return render(request, 'back/user_list.html')


def stop_simulation(request):
    """
        Called when stopping the simulation
    """
    res = manager.get_thread().stop_thread()
    manager.clear_paths()
    manager.clear_track_streams()
    manager.reset_thread()
    if res:
        return (HttpResponse('Stopped thread !', status=200))
    return (HttpResponse('Could not stop...', status=500))


def pause_simulation(request):
    """
        Called when pausing the simulation
    """
    res = manager.get_thread().pause()
    if res:
        return (HttpResponse('Paused thread !', status=200))
    return (HttpResponse('Could not pause...', status=500))


def play_simulation(request):
    """
        Called when restarting the simulation after a pause
    """
    res = manager.get_thread().play()
    if res:
        return (HttpResponse('Restarting thread !', status=200))
    return (HttpResponse('Could not pause...', status=500))


@csrf_exempt  # makes a security exception for this function to be triggered
def upload(request):
    """
        Deals with the upload and save of a PRP file so that the user can upload his own scenario
        :return: success if the file is safe and sound
    """
    if(request.method == 'POST'):
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():

            n_scenarios = 0
            for _, _, filenames in os.walk("scenarios/"):
                n_scenarios = len(filenames)
            if n_scenarios > 15:
                shutil.rmtree("scenarios/")

            fs = FileSystemStorage("scenarios/")
            manager.clear_paths()
            for key in request.FILES.keys():
                global_file = request.FILES[key]
                filename = fs.save(global_file.name, global_file)
                manager.add_path(os.path.join(fs.location, filename))
            for path in manager.get_paths():
                if path is not None:
                    track_stream = load.get_track_streams_from_prp(path)
                    manager.add_track_stream(track_stream)
            station_utils.sync_stations(*manager.get_track_streams())

        return(HttpResponse('POST ok !'))
    else:
        return(HttpResponse('POST failed'))
