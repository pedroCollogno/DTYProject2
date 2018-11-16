from django.conf.urls import url
from .views import user_list, startsimulation, upload, send_stations_positions


"""Routes for the websocket:
user_list is called whenever a user connects to localhost:8000/
test is the route used to send data to users connected with JSONs
"""

urlpatterns = [
    url(r'^$', user_list, name='user_list'),
    url(r'^startsimulation$', startsimulation, name="startsimulation"),
    url(r'^getstations$', send_stations_positions, name="get_stations"),
    url(r'^upload', upload, name="upload")
]
