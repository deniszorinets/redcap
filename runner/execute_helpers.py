# ssh
import paramiko
from Crypto.PublicKey import RSA

# IO
import io

# processes
import subprocess, os


def exec_on_remote(host: str, user: str, ssh_port: int, key: str, commands: [str], password=None) -> (int, str, str):
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
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command='\n'.join(commands))
    ssh_stdin.close()
    stdout = []
    stderr = []
    [stdout.append(line.decode('utf-8')) for line in ssh_stdout.read().splitlines()]
    [stderr.append(line.decode('utf-8')) for line in ssh_stderr.read().splitlines()]
    return ssh_stdout.channel.recv_exit_status(), '\n'.join(stdout), '\n'.join(stderr)


def exec_on_local(commands: [str]) -> [(str, str)]:
    """
    execute command on local host
    :param commands: commands to execute
    :return:
    """
    res = []
    p = subprocess.Popen("\n".join(commands), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ, shell=True)
    stdout, stderr = p.communicate()
    return p.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')


def prepare_output(res: tuple) -> (bool, dict, str):
    """
    prepare output
    :param res:
    :return:
    """
    success = True
    output = {'output': []}
    fail_stderr = None
    result_code, stdout, stderr = res
    output = {'stdout': stdout, 'stderr': stderr}
    if int(result_code) != 0:
        success = False
        fail_stderr = stderr
    return success, output, fail_stderr
