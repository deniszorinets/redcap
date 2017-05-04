from django.conf.urls import url, include
from .rest import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'playbook', PlaybookViewSet)
router.register(r'action_history', ActionHistoryViewSet)
router.register(r'build_target', BuildTargetViewSet)
router.register(r'build_group', BuildGroupViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
]