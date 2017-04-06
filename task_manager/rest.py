# models and fields
import json

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
    params = serializers.JSONField(allow_null=True)

    class Meta:
        model = BuildTarget
        fields = ('id', 'name', 'params', 'pipeline', 'project', 'server')


class BuildTargetParamsSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    additional_params = serializers.JSONField(allow_null=True)
    class Meta:
        fields = ('additional_params', )


class BuildGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BuildGroup
        fields = ('id', 'name', 'builds', 'parallel', 'trigger_on_success', 'trigger_on_fail')


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

    def get_serializer_class(self):
        if self.action == 'deploy':
            return BuildTargetParamsSerializer
        return BuildTargetSerializer  # I dont' know what you want for create/destroy/update

    @detail_route(methods=['post'])
    def deploy(self, request, pk: int=None):
        additional_params = request.data['additional_params']
        params = json.loads(additional_params)
        build_target_execute_async.apply_async(args=(pk, params))
        return Response({})


class BuildGroupViewSet(viewsets.ModelViewSet):
    queryset = BuildGroup.objects.all()
    serializer_class = BuildGroupSerializer

    @detail_route(methods=['post'])
    def deploy(self, request, pk: int = None):
        build_group_execute_async.apply_async(args=(pk, ))
        return Response({})
