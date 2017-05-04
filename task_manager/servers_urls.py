from django.conf.urls import url, include
from .rest import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'server', ServerViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
]