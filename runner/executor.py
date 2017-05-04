from redcap.celery import app
from celery import group
import runner.notifier as slack_notifier
import runner.custom_notifier as custom_notifier


from task_manager.models import BuildTarget, BuildGroup, Server

# logging
import logging
logger = logging.getLogger('systemwide')


@app.task(bind=True)
def build_target_execute_async(self, build_target_id: int, params: {}=None):
    try:
        build = BuildTarget.objects.get(id=build_target_id)
        slack_notifier.notify_started(build.server.name, build.project.url, build.project.title)
        res, stdout, stderr = build.execute(params)
        if res:
            slack_notifier.notify_success(build.server.name, build.project.url, build.project.title)
            custom_notifier.notify_success(self.request.id)
        else:
            slack_notifier.notify_fail(build.server.name, build.project.url, build.project.title, stderr)
            custom_notifier.notify_fail(self.request.id, stderr)
    except Exception as e:
        logger.error("Celery task: " + e.__str__())


@app.task(bind=True)
def build_group_execute_async(self, build_target_id: int):
    try:
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
    except Exception as e:
        logger.error("Celery task: " + e.__str__())

@app.task(bind=True)
def invalidate_server_key(self, server_id: int):
    try:
        server = Server.objects.get(id=server_id)
        server.invalidate_key()
    except Exception as e:
        logger.error("Celery task: " + e.__str__())
