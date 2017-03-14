# models and fields
from .models import *

# rest
from rest_framework import serializers, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

# celery tasks
from runner.executor import *


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'name', 'second_name', 'email', 'contacts')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'url', 'owner')


class PlaybookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Playbook
        fields = ('id', 'title', 'playbook', 'local')


class ActionHistorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ActionHistory
        fields = ('id', 'server', 'playbook', 'output', 'date')


class BuildTargetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BuildTarget
        fields = ('id', 'name', 'params', 'pipeline', 'project', 'server')


class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
        fields = (
            'id',
            'domain',
            'ip_v4',
            'ip_v6',
            'public_key',
            'name',
            'description',
            'username',
            'ssh_port'
        )
        read_only = ('public_key', )


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    @detail_route(methods=['get'])
    def invalidate(self, request, pk=None):
        invalidate_server_key.apply_async(args=(pk,))
        return Response({})


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class PlaybookViewSet(viewsets.ModelViewSet):
    queryset = Playbook.objects.all()
    serializer_class = PlaybookSerializer


class ActionHistoryViewSet(viewsets.ModelViewSet):
    queryset = ActionHistory.objects.all()
    serializer_class = ActionHistorySerializer


class BuildTargetViewSet(viewsets.ModelViewSet):
    queryset = BuildTarget.objects.all()
    serializer_class = BuildTargetSerializer

    @detail_route(methods=['get'])
    def deploy(self, request, pk=None):
        exec_server_playbook.apply_async(args=(pk,))
        return Response({})
