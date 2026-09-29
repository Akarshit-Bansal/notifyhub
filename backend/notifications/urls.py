from django.urls import path

from .views import (
    login_view,
    logout_view,
    me,
    triggers,
    template_list,
    test_send,
    logs,
    push_public_key,
    push_subscribe,
    health,
)

urlpatterns = [
    path("health/", health),
    path("login/", login_view),
    path("logout/", logout_view),
    path("me/", me),
    path("triggers/", triggers),
    path("templates/", template_list),
    path("test-send/", test_send),
    path("logs/", logs),
    path("push/public-key/", push_public_key),
    path("push/subscribe/", push_subscribe),
]