from django.db import models
from django.contrib.postgres import fields as psqlfields
from django.shortcuts import get_object_or_404
from ticket_scoring_api.utils import dotdict

# ------------------------- #

class TicketStatus(models.Model):

    ticket_status_id = models.SmallIntegerField()
    ticket_status = models.CharField(max_length=100)

    # ......................... #

    class Meta:
        db_table = 'static"."api_v1_ticket_status'

# ------------------------- #

class TicketType(models.Model):

    ticket_type_id = models.SmallIntegerField()
    ticket_type = models.CharField(max_length=100)

    # ......................... #

    class Meta:
        db_table = 'static"."api_v1_ticket_type'

# ------------------------- #
# Utils
# ------------------------- #

model_kv = dict(
        ticket_status=TicketStatus,
        ticket_type=TicketType
    )

def get_id_by_value(value, name: str) -> int:

    kwg = {name : value}
    obj = get_object_or_404(model_kv[name], **kwg)

    return int(getattr(obj, f'{name}_id'))

# ------------------------- #

def get_all_values(name: str) -> list:

    return model_kv[name].objects.values_list(name, flat=True)

# ------------------------- #