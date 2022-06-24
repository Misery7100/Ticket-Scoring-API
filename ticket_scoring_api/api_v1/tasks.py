import logging

from django_celery_beat.models import PeriodicTask, PeriodicTasks, IntervalSchedule
from ticket_scoring_api.celery import app as celery_app

# celery tasks, async stuff

logger = logging.getLogger(__name__)

@celery_app.task
def test(arg: str = 'test'):
    logger.warning(f'! {arg=} !')
