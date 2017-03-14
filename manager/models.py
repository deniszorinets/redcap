# models and fields
from django.db import models
import django.contrib.postgres.fields as psql

# vault
from redcap.vault import vault
from vault import VaultKeyManager

# django signals
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# L10n
from django.utils.translation import ugettext_lazy as _

# crypto helpers
import keymanager.helpers as rsa


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


@receiver(pre_delete)
def delete_repo(sender, instance, **kwargs):
    if sender == Server:
        vault.delete(str.format('secret/server_{0}', instance.id))
