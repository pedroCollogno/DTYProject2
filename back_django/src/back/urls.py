from django.conf.urls import url
from .views import user_list, start_simulation, stop_simulation, upload, send_stations_positions, initiate_emittors_positions


"""Routes for the websocket:
user_list is called whenever a user connects to localhost:8000/
test is the route used to send data to users connected with JSONs
"""

urlpatterns = [
    url(r'^$', user_list, name='user_list'),
    url(r'^startsimulation$', start_simulation, name="startsimulation"),
    url(r'^startsimulationML$', start_simulation, name="startsimulationML"),
    url(r'^startsimulationDL$', start_simulation, name="startsimulationDL"),
    url(r'^stopsimulation$', stop_simulation, name="stopsimulation"),
    url(r'^getstations$', send_stations_positions, name="get_stations"),
    url(r'^emittorspositions$', initiate_emittors_positions,
        name="emittors_positions"),
    url(r'^upload', upload, name="upload")
]
