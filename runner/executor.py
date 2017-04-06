from redcap.celery import app
from celery import group
from runner.notifier import notify_success, notify_fail, notify_started


from task_manager.models import BuildTarget, BuildGroup, Server


@app.task(bind=True)
def build_target_execute_async(self, build_target_id: int, params: {}=None):
    build = BuildTarget.objects.get(id=build_target_id)
    notify_started(build.server.name, build.project.url, build.project.title)
    res, stdout, stderr = build.execute(params)
    if res:
        notify_success(build.server.name, build.project.url, build.project.title)
    else:
        notify_fail(build.server.name, build.project.url, build.project.title, stderr)


@app.task(bind=True)
def build_group_execute_async(self, build_target_id: int):
    build = BuildGroup.objects.get(id=build_target_id)
    if not bool(build.parallel):
        res = build.execute()
        if res is None:
            if build.trigger_on_success is not None:
                build_group_execute_async.apply_async(args=(build.trigger_on_success.id, ))
        else:
            if build.trigger_on_fail is not None:
                build_group_execute_async.apply_async(args=(build.trigger_on_fail.id, ))
    else:
        builds = build.builds.order_by('groupbuildpipeline__order').all()
        job = group(build_target_execute_async.s(b.id) for b in builds)
        job.apply_async()


@app.task(bind=True)
def invalidate_server_key(self, server_id: int):
    server = Server.objects.get(id=server_id)
    server.invalidate_key()

