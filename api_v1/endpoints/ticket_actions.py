import json
import logging

from datetime import datetime, timezone
from django.shortcuts import get_object_or_404
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api_v1.models.dynamic import *
from api_v1.models.static import *
from api_v1.serializers import *
from api_v1.scoring.preprocess_ticket_data import preprocess_ticket_data
from api_v1.tasks import update_ticket_score

# ------------------------- #

logger = logging.getLogger(__name__)

# ------------------------- #

@api_view(http_method_names=['POST'])
def add_ticket(request: Request) -> Response:
    """
    Register (add) a ticket for periodical scoring.

    Args:
        request (Request): external request

    Returns:
        Response:
            400: ValueError
            201: ticket successfully added
    """

    # note: dotdict broke serializing
    data = request.data

    ticket_type = data['ticket_type']
    ticket_id = data['ticket_id']

    # unsync between staticdata and serializers mb
    if ticket_type not in get_all_values(name='ticket_type'):
        return Response(
            status=status.HTTP_400_BAD_REQUEST, 
            data={'ticket_type' : ['unknown ticket_type']}) # TODO: better error handling

    # take type id from static table
    data['ticket_type_id'] = get_id_by_value(ticket_type, name='ticket_type')

    # store ticket globally if data is valid
    ticket = TicketSerializer(data=data)
    ticket.is_valid(raise_exception=True) # raises 400 if invalid
    ticket.save()
    
    # add new data for storing type-specific stuff
    data['ticket_assigned'] = ticket_id

    # build data due non-flat request schema 
    # for some ticket types
    type_specific = preprocess_ticket_data(data, ticket_type)

    if type_specific.is_valid():

        # save if data is valid
        type_specific.save()

        # schedule a task to update ticket score:
        # 1. get or create a schedule
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=5, 
            period=IntervalSchedule.SECONDS, # TODO: change period from service endpoint <-
        )

        # 2. create a periodic task with assigned function
        PeriodicTask.objects.create(
            interval=schedule,
            name=f'api_v1.update_ticket_score[{ticket_id}]',
            task='api_v1.tasks.update_ticket_score', 
            args=json.dumps([data['ticket_type_id'], data['ticket_id']]),
            kwargs=json.dumps(type_specific.data)
        )

        # 3. first score calculation async
        update_ticket_score.apply_async(
            args=[data['ticket_type_id'], data['ticket_id']],
            kwargs=type_specific.data, 
            countdown=10 # 10 seconds countdown before calculate and push to Spell
        )

        return Response(
            data={'ticket_id' : ticket_id}, 
            status=status.HTTP_201_CREATED
        )
    
    else:
        Ticket.objects.get(ticket_id=ticket_id).delete()
        type_specific.is_valid(raise_exception=True)

# ------------------------- #

@api_view(http_method_names=['POST'])
def pause_ticket(request: Request, ticket_id: str) -> Response:
    """
    _summary_

    Args:
        request (Request): external request
        ticket_id (str): ticket ID in the universal format

    Returns:
        Response:
            404:
            400:
            200:dw
    """

    # get ticket globally
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    # raise error if ticket isn't active
    if ticket.ticket_status_id != get_id_by_value('active', name='ticket_status'):
        return Response(
            status=status.HTTP_400_BAD_REQUEST, 
            data={'ticket_id' : ticket_id, 'ticket_status' : ['ticket already paused or closed']})

    else:
        # else store new pause timestamp
        pause_time = datetime.now(timezone.utc)
        ticket.last_pause_timestamp = pause_time

        # update ticket status
        ticket.ticket_status_id = get_id_by_value('paused', name='ticket_status')
        ticket.save()

        # pause assigned update task
        task = PeriodicTask.objects.get(name=f'api_v1.update_ticket_score[{ticket.ticket_id}]')
        task.enabled = False
        task.save()

        return Response(status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['POST'])
def resume_ticket(request: Request, ticket_id: str) -> Response:
    """
    _summary_

    Args:
        request (Request): external request
        ticket_id (str): ticket ID in the universal format

    Returns:
        Response:
            404:
            400:
            200:
    """

    # get ticket globally
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

    # raise error if ticket isn't paused
    if ticket.ticket_status_id != get_id_by_value('paused', name='ticket_status'):
        return Response(
            status=status.HTTP_400_BAD_REQUEST, 
            data={'ticket_id' : ticket_id, 'ticket_status' : ['ticket already active or closed']})
    
    else:
        # else update total hours in pause
        resume_time = datetime.now(timezone.utc)
        in_pause = ticket.hours_in_pause
        delta = resume_time - ticket.last_pause_timestamp
        in_pause += delta.days * 24 + delta.seconds / 3600
        ticket.hours_in_pause = in_pause

        # update ticket status
        ticket.ticket_status_id = get_id_by_value('active', name='ticket_status')
        ticket.save()

        # resume assigned update task
        task = PeriodicTask.objects.get(name=f'api_v1.update_ticket_score[{ticket.ticket_id}]')
        task.enabled = True
        task.save()

        return Response(status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['POST'])
def close_ticket(request: Request, ticket_id: str) -> Response:
    """
    _summary_

    Args:
        request (Request): external request
        ticket_id (str): ticket ID in the universal format

    Returns:
        Response:
            404:
            400:
            200:
    """

    # get ticket globally
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    # raise error if ticket isn't active
    if ticket.ticket_status_id != get_id_by_value('active', name='ticket_status'):
        return Response(
            status=status.HTTP_400_BAD_REQUEST, 
            data={'ticket_id' : ticket_id, 'ticket_status' : ['ticket in pause or already closed']})
        
    else:
        # else determine solving date
        solving_date = datetime.now(timezone.utc)
        ticket.solving_date = solving_date

        # update ticket status
        ticket.ticket_status_id = get_id_by_value('closed', name='ticket_status')
        ticket.save()

        # delete assigned update task
        PeriodicTask.objects.get(name=f'api_v1.update_ticket_score[{ticket.ticket_id}]').delete()

        return Response(status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['GET'])
def get_ticket(request: Request, ticket_id: str) -> Response:
    """
    _summary_

    Args:
        request (Request): external request
        ticket_id (str): ticket ID in the universal format

    Returns:
        Response:
            404:
            200:
    """

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    ticket = TicketSerializer(ticket)

    return Response(data=ticket.data, status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['DELETE'])
def delete_ticket(request: Request, ticket_id: str) -> Response:
    """
    _summary_

    Args:
        request (Request): external request
        ticket_id (str): ticket ID in the universal format

    Returns:
        Response:
            404:
            200:
    """

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

    if ticket.ticket_status_id != get_id_by_value('closed', name='ticket_status'):
        PeriodicTask.objects.get(name=f'api_v1.update_ticket_score[{ticket.ticket_id}]').delete()

    ticket.delete()

    return Response(status=status.HTTP_200_OK)

# ------------------------- #