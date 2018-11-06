from django.conf.urls import url
from back.views import user_list,test

"""Routes for the websocket:
user_list is called whenever a user connects to localhost:8000/
test is the route used to send data to users connected with JSONs"""

urlpatterns = [
    url(r'^$', user_list, name='user_list'),
    url(r'^test$',test, name="test" )
]
