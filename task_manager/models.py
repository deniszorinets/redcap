# models and fields
from celery import group
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
import django.contrib.postgres.fields as psql

# vault
from jinja2 import Template

from redcap.vault import vault
from vault import VaultKeyManager

# django signals
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# L10n
from django.utils.translation import ugettext_lazy as _

# crypto helpers
import keymanager.helpers as rsa

from runner.execute_helpers import exec_on_local, exec_on_remote, prepare_output


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    second_name = models.CharField(max_length=64)
    email = models.EmailField(null=True, default=None, blank=True)
    contacts = psql.JSONField(null=True, default=None, blank=True)

    def __str__(self):
        return str.format("{0} {1}", self.name, self.second_name)

    class Meta:
        db_table = 'manager_clients'
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.TextField(null=True, default=None, blank=True)
    url = models.URLField(null=True, default=None, blank=True)
    owner = models.ForeignKey('Client', null=True, default=None, blank=True)

    class Meta:
        db_table = 'manager_projects'
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __str__(self):
        return self.title.__str__()


class Playbook(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)
    playbook = models.TextField()
    local = models.BooleanField(default=False)

    class Meta:
        db_table = 'manager_playbooks'
        verbose_name = _('Playbook')
        verbose_name_plural = _('Playbooks')

    def __str__(self):
        return self.title.__str__()

    def execute(self, host: str, user: str, ssh_port: int, key: str, params: dict, password=None) -> (int, str, str):
        template = Template(self.playbook)
        commands = template.render(params).splitlines()

        if not self.local:
            res = exec_on_remote(host, user, ssh_port, key, commands, password)
        else:
            res = exec_on_local(commands)

        return res


class Server(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=256)
    ssh_port = models.IntegerField(default=22)
    domain = models.CharField(null=True, default=None, blank=True, max_length=256)
    ip_v4 = models.GenericIPAddressField(null=True, default=None, blank=True)
    ip_v6 = models.GenericIPAddressField(null=True, default=None, blank=True)
    private_key = models.TextField(null=True, default=None, blank=True)
    public_key = models.TextField(null=True, default=None, blank=True)
    name = models.CharField(max_length=32)
    description = models.TextField(null=True, default=None, blank=True)

    def save(self, **kwargs):
        super(Server, self).save()
        if self.private_key is None or self.public_key is None:
            self.invalidate_key()

    @property
    def key_pass(self) -> str or None:
        if self.id is not None:
            return VaultKeyManager(vault).get(str.format('secret/server_{0}', self.id))['data']['key']
        return None

    def invalidate_key(self) -> None:
        if self.id is not None:
            new_key_pass = rsa.random_key(64)
            self.private_key, self.public_key = rsa.opsenssh_keypair(new_key_pass)
            VaultKeyManager(vault).set(str.format('secret/server_{0}', self.id), key=new_key_pass)
            self.save()

    def __str__(self) -> str:
        return self.name.__str__()

    class Meta:
        db_table = 'manager_servers'
        verbose_name = _('Server')
        verbose_name_plural = _('Servers')


class BuildPipeline(models.Model):
    playbook = models.ForeignKey('Playbook')
    build_target = models.ForeignKey('BuildTarget')
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.playbook.__str__()

    class Meta:
        db_table = 'manager_build_pipeline'
        unique_together = ('playbook', 'build_target')
        verbose_name = _('Server pipeline')
        verbose_name_plural = _('Server pipeline')
        ordering = ('order',)


class BuildTarget(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    params = psql.JSONField(null=True, default=None, blank=True)
    pipeline = models.ManyToManyField('Playbook', through='BuildPipeline', through_fields=('build_target', 'playbook'))
    project = models.ForeignKey('Project')
    server = models.ForeignKey('Server')

    def __str__(self):
        return self.name.__str__()

    def execute(self, params: {} = None) -> (int, str, str):
        playbooks = self.pipeline.order_by('buildpipeline__order').all()
        if playbooks is None:
            raise ObjectDoesNotExist(str.format('playbooks for server with id {0} not found', self.server.id))

        server = self.server
        host = None
        fail_stderr = None
        output = None
        success = True
        if server.ip_v4 is not None:
            host = server.ip_v4
        elif server.ip_v6 is not None:
            host = server.ip_v6
        elif server.domain is not None:
            host = server.domain

        if params is not None:
            parameters = {**self.params, **params}
        else:
            parameters = self.params

        for playbook in playbooks:
            res = playbook.execute(host,
                                   server.username,
                                   server.ssh_port,
                                   server.private_key,
                                   parameters,
                                   server.key_pass)

            _success, _output, _fail_stderr = prepare_output(res)
            ActionHistory(output=_output, server=server, playbook_id=playbook.id).save()
            if not _success:
                success = False
                output = _output
                fail_stderr = _fail_stderr
                break
        return success, output, fail_stderr

    class Meta:
        db_table = 'manager_build_targets'
        verbose_name = _('Build Target')
        verbose_name_plural = _('Build Targets')


class ActionHistory(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey('Server')
    playbook = models.ForeignKey('Playbook')
    output = psql.JSONField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.date.__str__()

    class Meta:
        db_table = 'manager_servers_action_history'
        verbose_name = _('Action history')
        verbose_name_plural = _('Action history')


class GroupBuildPipeline(models.Model):
    group = models.ForeignKey('BuildGroup')
    build = models.ForeignKey('BuildTarget')
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.build.name.__str__()

    class Meta:
        db_table = 'manager_group_build_pipeline'
        unique_together = ('group', 'build')
        verbose_name = _('Group pipeline')
        verbose_name_plural = _('Group pipeline')
        ordering = ('order',)


class BuildGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    builds = models.ManyToManyField('BuildTarget', through='GroupBuildPipeline', through_fields=('group', 'build'))
    parallel = models.BooleanField(default=False)
    trigger_on_success = models.ForeignKey('BuildGroup', related_name='success_trigger', null=True, blank=True)
    trigger_on_fail = models.ForeignKey('BuildGroup', related_name='fail_trigger', null=True, blank=True)

    def __str__(self):
        return self.name.__str__()

    @staticmethod
    def errors(res: [(int, str, str)]) -> [(bool, str, str)]:
        result = []
        if res is not None:
            for r, i, o in res:
                if r != 0:
                    result.append((False, i, o))
        return result

    def execute(self) -> [(int, str, str)]:
        builds = self.builds.order_by('groupbuildpipeline__order').all()
        res = []
        for build in builds:
            res.append(build.execute())
        errors = BuildGroup.errors(res)
        if errors.__len__() > 0:
            return errors
        return None

    class Meta:
        db_table = 'manager_group'
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')


@receiver(pre_delete)
def delete_repo(sender, instance, **kwargs):
    if sender == Server:
        vault.delete(str.format('secret/server_{0}', instance.id))
