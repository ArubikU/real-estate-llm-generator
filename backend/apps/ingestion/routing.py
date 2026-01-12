"""
WebSocket routing for the ingestion app.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/progress/(?P<task_id>[^/]+)/$', consumers.ProgressConsumer.as_asgi()),
]
