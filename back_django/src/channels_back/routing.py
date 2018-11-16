from channels.routing import route
from back import ws_connect, ws_disconnect

"""Specific routes for the websocket"""
channel_routing = [
    route('websocket.connect', ws_connect),
    route('websocket.disconnect', ws_disconnect)
]
