# ssh
import paramiko
from Crypto.PublicKey import RSA

# IO
import io

# models
import manager.models as manager_models

#templates
from jinja2 import Template

# messenger
from .notifier import *

# celery
from redcap.celery import app

# exceptions
from paramiko.ssh_exception import AuthenticationException
from django.core.exceptions import ObjectDoesNotExist

# processes
import subprocess


def exec_on_remote(host: str, user: str, ssh_port: int, key: str, commands: [str], password=None) -> [(str, str)]:
    """
    execute command on remove host
    :param ssh_port: ssh port
    :param host: host
    :param user: username
    :param key: private key
    :param commands: commands to execute
    :param password: password to encrypted private key
    :return:
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    private_key = RSA.importKey(externKey=key, passphrase=password)

    f = io.StringIO(private_key.exportKey().decode(), newline=None)

    private_key = paramiko.RSAKey.from_private_key(f)

    ssh.connect(host, username=user, pkey=private_key, port=ssh_port)
    res = []
    for command in commands:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command=command)
        ssh_stdin.close()
        stdout = []
        stderr = []
        [stdout.append(line.decode('utf-8')) for line in ssh_stdout.read().splitlines()]
        [stderr.append(line.decode('utf-8')) for line in ssh_stderr.read().splitlines()]
        res.append(('\n'.join(stdout), '\n'.join(stderr)))
    return res


def exec_on_local(commands: [str]) -> [(str, str)]:
    """
    execute command on local host
    :param commands: commands to execute
    :return:
    """
    res = []
    for command in commands:
        p = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        res.append((stdout.decode('utf-8'), stderr.decode('utf-8')))
    return res


def prepare_output(res: [tuple]) -> (bool, dict, str):
    """
    prepare output
    :param res:
    :return:
    """
    success = True
    output = {'output': []}
    fail_stderr = None
    for i in range(res.__len__()):
        stdout, stderr = res[i]
        output['output'].append({'line': i + 1, 'output': {'stdout': stdout, 'stderr': stderr}})
        if not (stderr == '' or stderr is None):
            success = False
            fail_stderr = stderr
            break
    return success, output, fail_stderr


@app.task(bind=True)
def exec_server_playbook(self, build_target: int) -> [([str], [str])]:
    """
    execute server playbook
    :param self: celery task
    :param build_target: build target id
    :return:
    """
    server_build = manager_models.BuildTarget.objects.filter(id=build_target).first()
    server = server_build.server
    host = None
    if server.ip_v4 is not None:
        host = server.ip_v4
    elif server.ip_v6 is not None:
        host = server.ip_v6
    elif server.domain is not None:
        host = server.domain

    project = server_build.project
    project_url = project.url
    project_name = project.__str__()
    notify_started(server.name, project_url, project_name)

    scripts = manager_models.BuildPipeline.objects.filter(
        build_target__id=server_build.id).order_by('order').all().values_list('playbook__playbook', 'playbook__id', 'playbook__local')
    if scripts is None:
        raise ObjectDoesNotExist(str.format('playbooks for server with id {0} not found', build_target))
    success = True
    fail_output = None
    for script, playbook_id, local in scripts:
        template = Template(script)
        commands = template.render(server_build.params).splitlines()
        if local:
            try:
                res = exec_on_local(commands)
            except Exception as e:
                fail_output = e.__str__()
                success = False
                break
        else:
            try:
                res = exec_on_remote(
                    host,
                    server.username,
                    server.ssh_port,
                    server.private_key,
                    commands,
                    server.key_pass)
            except AuthenticationException:
                fail_output = "Authentication failed"
                success = False
                break
            except Exception as e:
                fail_output = e.__str__()
                success = False
                break

        success, output, fail_stderr = prepare_output(res)
        manager_models.ActionHistory(
            output=output, server=server, playbook_id=playbook_id).save()
        if not success:
            fail_output = fail_stderr
            break
    if success:
        notify_success(server.name, project_url, project_name)
    else:
        notify_fail(server.name, project_url, project_name, fail_output)


@app.task(bind=True)
def invalidate_server_key(self, server_id: int) -> None:
    """
    create new keypair for server
    :param self: celery task
    :param server_id: server id
    :return:
    """
    server = manager_models.Server.objects.filter(id=server_id).first()
    server.invalidate_key()
