from __future__ import absolute_import

from pubbot.main.celery import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(subscribe=['#'])
def log_everything(msg):
    logger.info(msg)
