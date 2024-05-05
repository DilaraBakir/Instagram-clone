from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/notifications/<str:id>", consumers.NotificationConsumer.as_asgi()),
]

