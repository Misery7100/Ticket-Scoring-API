import os
import yaml

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from pathlib import Path

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent.parent.parent  #! ah shit dude

with open(os.path.join(BASE_DIR, 'secret/staticdata.yml'), 'r') as stream:
    staticdata = yaml.safe_load(stream)

# ------------------------- #

def insert_initial_data(sender, **kwargs):

    from ticket_scoring_api.api_v1 import static_models, models

    # ......................... #

    def create(model, **kwargs):
        model.objects.get_or_create(**kwargs)

    # ......................... #

    for key, value in staticdata['ticket_status'].items():
        create(static_models.TicketStatus, ticket_status_id=value, ticket_status=key)
    
    for key, value in staticdata['ticket_type'].items():
        create(static_models.TicketType, ticket_type_id=value, ticket_type=key)
    
    for key, value in staticdata['avg_solving_time'].items():
        create(models.AverageSolvingTime, ticket_type_id=key, avg_solving_time_hours=value)

# ------------------------- #

class ApiV1Config(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticket_scoring_api.api_v1'

    # ......................... #

    def ready(self) -> None:
        post_migrate.connect(insert_initial_data, sender=self)
