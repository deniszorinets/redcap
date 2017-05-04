import json
from django.http import JsonResponse
from runner.executor import *

ERROR_STATE = 500
SUCCESS_STATE = 200
NO_AUTH_STATE = 401

class AsyncState:
    id = None


def deploy(request):
    if not request.user.is_authenticated():
        return JsonResponse({'status': NO_AUTH_STATE, 'error': 'not authorized'})
    async_state = AsyncState()
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        try:
            server_build_id = int(data['serverID'])
            state = build_target_execute_async.apply_async(args=(server_build_id, ))
            async_state.id = state.id
        except ValueError:
            return JsonResponse({'id': async_state.id, 'status': ERROR_STATE, 'error': 'build id is not valid'})
        except Exception as e:
            return JsonResponse({'id': async_state.id, 'status': ERROR_STATE, 'error': e.__str__()})

    return JsonResponse({'id': async_state.id, 'status': SUCCESS_STATE})


def deploy_group(request):
    if not request.user.is_authenticated():
        return JsonResponse({'status': NO_AUTH_STATE, 'error': 'not authorized'})
    async_state = AsyncState()
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        try:
            server_group_build_id = int(data['serverID'])
            state = build_group_execute_async.apply_async(args=(server_group_build_id, ))
            async_state.id = state.id
        except ValueError:
            return JsonResponse({'id': async_state.id, 'status': ERROR_STATE, 'error': 'group id is not valid'})
        except Exception as e:
            return JsonResponse({'id': async_state.id, 'status': ERROR_STATE, 'error': e.__str__()})

    return JsonResponse({'id': async_state.id, 'status': SUCCESS_STATE})


def invalidate(request):
    if not request.user.is_authenticated():
        return JsonResponse({'status': NO_AUTH_STATE, 'error': 'not authorized'})

    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        try:
            server_id = int(data['serverID'])
            invalidate_server_key.apply_async(args=(server_id, ))
        except ValueError:
            return JsonResponse({'status': ERROR_STATE, 'error': 'server id is not valid'})
        except Exception as e:
            return JsonResponse({'status': ERROR_STATE, 'error': e.__str__()})

    return JsonResponse({'status': SUCCESS_STATE})