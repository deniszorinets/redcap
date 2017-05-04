#!/usr/bin/env bash
rabbitmqctl add_user celery celery
rabbitmqctl add_vhost celery
rabbitmqctl set_user_tags celery celery
rabbitmqctl set_permissions -p celery celery ".*" ".*" ".*"