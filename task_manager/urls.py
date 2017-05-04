from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^deploy/$', views.deploy),
    url(r'^deploy_group/$', views.deploy_group),
    url(r'^invalidate/$', views.invalidate),
]