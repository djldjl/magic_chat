from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # 对应地址 ws://127.0.0.1:8000/ws/chat/
    path("ws/chat/", consumers.ChatConsumer)
]
