# I wrote this code

from channels.routing import ProtocolTypeRouter, URLRouter
import social_app.routing
from django.urls import path

application = ProtocolTypeRouter({
    'websocket': URLRouter(
        social_app.routing.websocket_urlpatterns
    ),
})

# end of code I wrote