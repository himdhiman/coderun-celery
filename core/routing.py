from django.urls import path
from core import consumers

ws_urlpatterns = [path("ws/runcode/<str:uid>/", consumers.CodeRunConsumer.as_asgi())]
