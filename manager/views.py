import json
from django.http import JsonResponse
from runner.executor import *


def deploy(request):
    if not request.user.is_authenticated():
        return JsonResponse({'status': 401, 'error': 'not authorized'})

    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        try:
            server_build_id = int(data['serverID'])
            exec_server_playbook.apply_async(args=(server_build_id, ))
        except ValueError:
            return JsonResponse({'status': 500, 'error': 'server id is not valid'})
        except Exception as e:
            return JsonResponse({'status': 500, 'error': e.__str__()})

    return JsonResponse({'status': 'ok'})


def invalidate(request):
    if not request.user.is_authenticated():
        return JsonResponse({'status': 401, 'error': 'not authorized'})

    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        try:
            server_id = int(data['serverID'])
            invalidate_server_key.apply_async(args=(server_id, ))
        except ValueError:
            return JsonResponse({'status': 500, 'error': 'server id is not valid'})
        except Exception as e:
            return JsonResponse({'status': 500, 'error': e.__str__()})

    return JsonResponse({'status': 'ok'})