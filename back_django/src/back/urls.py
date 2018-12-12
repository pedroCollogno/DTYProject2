from django.conf.urls import url
from .views import *


"""Routes for the websocket:
    user_list is called whenever a user connects to localhost:8000/
    test is the route used to send data to users connected with JSONs
"""

urlpatterns = [
    url(r'^$', user_list, name='user_list'),
    url(r'^startsimulation$', start_simulation, name="startsimulation"),
    url(r'^startsimulationMix$', start_simulation_mix, name="startsimulationMix"),
    url(r'^startsimulationML$', start_simulation_ml, name="startsimulationML"),
    url(r'^startsimulationDL$', start_simulation_dl, name="startsimulationDL"),
    url(r'^stopsimulation$', stop_simulation, name="stopsimulation"),
    url(r'^pausesimulation$', pause_simulation, name="pausesimulation"),
    url(r'^playsimulation$', play_simulation, name="playsimulation"),
    url(r'^getstations$', send_stations_positions, name="get_stations"),
    url(r'^emitterspositions$', initiate_emitters_positions,
        name="emitters_positions"),
    url(r'^upload', upload, name="upload")
]
