import os
import yaml

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from pathlib import Path

from ticket_scoring_api.local import *

# ------------------------- #

def insert_initial_data(sender, **kwargs):

    from api_v1.models import static
    from api_v1.models import dynamic

    def create(model, **kwargs):
        model.objects.get_or_create(**kwargs)

    # ......................... #

    for key, value in staticdata.ticket_status.items():
        create(static.TicketStatus, ticket_status_id=value, ticket_status=key)
    
    for key, value in staticdata.ticket_type.items():
        create(static.TicketType, ticket_type_id=value, ticket_type=key)
    
    for key, value in staticdata.avg_solving_time.items():
        create(dynamic.AverageSolvingTime, ticket_type_id=key, avg_solving_time_hours=value)

# ------------------------- #

class ApiV1Config(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api_v1'

    # ......................... #

    def ready(self) -> None:
        post_migrate.connect(insert_initial_data, sender=self)
