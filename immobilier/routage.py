from django.urls import re_path

from .consommateurs import ConsommateurConversation


urlpatterns = [
    re_path(r'^ws/messages/conversation/(?P<identifiant_conversation>\d+)/$', ConsommateurConversation.as_asgi()),
]
