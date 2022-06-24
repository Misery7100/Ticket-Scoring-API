import logging
import os
import requests
import yaml

from datetime import datetime, timezone
from django.shortcuts import get_object_or_404
from django_celery_beat.models import PeriodicTask, PeriodicTasks, IntervalSchedule
from pathlib import Path
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from ticket_scoring_api.api_v1.models import *
from ticket_scoring_api.api_v1.static_models import *
from ticket_scoring_api.api_v1.serializers import *
from ticket_scoring_api.celery import app as celery_app

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent #! ah shit dude

with open(os.path.join(BASE_DIR, 'secret/credentials.yml'), 'r') as stream:
    creds = yaml.safe_load(stream)

# ------------------------- #

@api_view(http_method_names=['POST'])
def add_ticket(request):

    ticket_type = request.data['ticket_type']
    ticket_id = request.data['ticket_id']

    # unsync between staticdata and serializers mb
    if ticket_type not in get_all_values(name='ticket_type'):
        return Response(
            status=status.HTTP_400_BAD_REQUEST, 
            data={'ticket_type' : ['unknown ticket type']})

    data = {**request.data, 'ticket_type_id' : get_id_by_value(ticket_type, name='ticket_type')}

    ticket = TicketSerializer(data=data)
    ticket.is_valid(raise_exception=True)
    ticket.save()
    
    data = {**data, 'ticket_assigned' : ticket_id}
    type_specific = ticket_data_build(data, ticket_type)

    if type_specific.is_valid():
        type_specific.save()

        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.SECONDS,
        )

        PeriodicTask.objects.get_or_create(
            interval=schedule,                  # we created this above.
            name=f'updating {ticket_id}',          # simply describes this periodic task.
            task='ticket_scoring_api.api_v1.tasks.test',  # name of task.
            args=f'["{ticket_id} is on updating"]'
        )

        return Response(data={'ticket_id' : ticket_id}, status=status.HTTP_201_CREATED)
    
    else:
        Ticket.objects.get(ticket_id=ticket_id).delete()
        type_specific.is_valid(raise_exception=True)
    
    # TODO: scoring and saving result into ScoringGlobal

# ------------------------- #

@api_view(http_method_names=['POST'])
def pause_ticket(request, ticket_id: str):

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    if ticket.ticket_status_id != get_id_by_value('active', name='ticket_status'):
        return Response(
            status=status.HTTP_400_BAD_REQUEST, 
            data={'ticket_id' : ticket_id, 'ticket_status' : ['ticket already paused or closed']})

    else:
        pause_time = datetime.now(timezone.utc)
        ticket.last_pause_timestamp = pause_time
        ticket.ticket_status_id = get_id_by_value('paused', name='ticket_status')
        ticket.save()

        return Response(status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['POST'])
def resume_ticket(request, ticket_id: str):

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

    if ticket.ticket_status_id != get_id_by_value('paused', name='ticket_status'):
        return Response(
            status=status.HTTP_400_BAD_REQUEST, 
            data={'ticket_id' : ticket_id, 'ticket_status' : ['ticket already active or closed']})
    
    else:
        resume_time = datetime.now(timezone.utc)
        in_pause = ticket.hours_in_pause
        delta = resume_time - ticket.last_pause_timestamp
        in_pause += delta.days * 24 + delta.seconds / 3600

        ticket.hours_in_pause = in_pause
        ticket.ticket_status_id = get_id_by_value('active', name='ticket_status')
        ticket.save()

        return Response(status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['POST'])
def close_ticket(request, ticket_id: str):

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    # TODO: avoid replication
    if ticket.ticket_status_id != get_id_by_value('active', name='ticket_status'):
        return Response(
            status=status.HTTP_400_BAD_REQUEST, 
            data={'ticket_id' : ticket_id, 'ticket_status' : ['ticket in pause or already closed']})
        
    else:
        solving_date = datetime.now(timezone.utc)
        ticket.solving_date = solving_date
        ticket.ticket_status_id = get_id_by_value('closed', name='ticket_status')
        ticket.save()

        PeriodicTask.objects.get(name=f'updating {ticket.ticket_id}').delete()

        return Response(status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['GET'])
def get_ticket(request, ticket_id: str):

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    ticket = TicketSerializer(ticket)

    return Response(data=ticket.data, status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['DELETE'])
def delete_ticket(request, ticket_id: str):

    get_object_or_404(Ticket, ticket_id=ticket_id).delete()

    return Response(status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['POST'])
def update_ticket_score(request, ticket_id: str):

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    # TODO: avoid too often repeat
    # ... scoring

    return Response(status=status.HTTP_200_OK)

# ------------------------- #
# Utils
# ------------------------- #

def ticket_data_build(data, ticket_type):

    result = SERIALIZERS[ticket_type](data=data)

    # if ticket_type_id == 'verify_profile':
    #     pass

    return result

# ------------------------- #

def convert_currency_to_eur(amount: float, currency: str, credentials=creds):

    creds = creds['alphavantage']
    url = f'{creds["url"]}&from_currency={currency}&to_currency=EUR&apikey={creds["api_key"]}'
    res = requests.get(url)
    result = res.json()

    exchange_rate = float(result['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    converted = amount * exchange_rate

    return converted

# ------------------------- #