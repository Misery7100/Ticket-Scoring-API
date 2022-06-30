import os
import yaml

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from pathlib import Path

from backend.local import *

# ------------------------- #

def insert_initial_data(sender: AppConfig, **kwargs):
    """
    Populate initial data for common small tables using local yml files.

    Args:
        sender (AppConfig): app-related config instance
    """

    from api_v1.models import static
    from api_v1.models import dynamic

    def populate(model, **kwargs):
        model.objects.get_or_create(**kwargs)

    # ......................... #

    for key, value in staticdata.ticket_status.items():
        populate(static.TicketStatus, ticket_status_id=value, ticket_status=key)
    
    for key, value in staticdata.ticket_type.items():
        populate(static.TicketType, ticket_type_id=value, ticket_type=key)
    
    for key, value in staticdata.avg_solving_time.items():
        populate(dynamic.AverageSolvingTime, ticket_type_id=key, avg_solving_time_hours=value)
    
    for key, value in staticdata.max_relative_score.items():
        populate(dynamic.MaxRelativeScore, ticket_type_id=key, max_relative_score=value)

# ------------------------- #

def setup_routine_tasks():
    """
    Configure routine periodical tasks with celery and django_celery_beat.
    """

    from django_celery_beat.models import PeriodicTask, IntervalSchedule

    # ......................... #

    # average solving time update

    schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.HOURS, # TODO: change period from service endpoint <-
        )

    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='api_v1.tasks.update_average_solving_time',
        task='api_v1.tasks.update_average_solving_time'
    )

# ------------------------- #

class ApiV1Config(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api_v1'

    # ......................... #

    def ready(self) -> None:
        post_migrate.connect(insert_initial_data, sender=self)

        # if reset
        try:
            setup_routine_tasks()
        except:
            pass
