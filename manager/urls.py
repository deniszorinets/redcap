from django.conf.urls import url, include
from . import views
from .rest import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'server', ServerViewSet)
router.register(r'project', ProjectViewSet)
router.register(r'client', ClientViewSet)
router.register(r'playbook', PlaybookViewSet)
router.register(r'action_history', ActionHistoryViewSet)
router.register(r'build_target', BuildTargetViewSet)


urlpatterns = [
    url(r'^deploy/$', views.deploy),
    url(r'^invalidate/$', views.invalidate),
    url(r'^', include(router.urls)),
]