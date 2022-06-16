from datetime import datetime, timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .models import *
from .serializers import *

# ------------------------- #

@api_view(http_method_names=['POST'])
def add_ticket(request):

    ticket = TicketSerializer(data=request.data)
    ticket.is_valid(raise_exception=True)

    ticket_type = request.data['ticket_type']
    ticket_id = request.data['ticket_id']

    if ticket_type not in SERIALIZERS.keys():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    ticket.save()
    data = {**request.data, 'ticket_assigned' : ticket_id}
    type_specific = SERIALIZERS[ticket_type](data=data)

    if type_specific.is_valid():
        type_specific.save()
    
    else:
        Ticket.objects.get(ticket_id=ticket_id).delete()
        type_specific.is_valid(raise_exception=True)
    
    # TODO: scoring and saving result into ScoringGlobal

    return Response(data={'global' : ticket.data, 'type-specific' : type_specific.data}, status=status.HTTP_201_CREATED)

# ------------------------- #

@api_view(http_method_names=['POST'])
def pause_ticket(request, ticket_id: str):

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
   
    pause_time = datetime.now(timezone.utc)
    ticket.last_pause_timestamp = pause_time
    ticket.save()

    return Response(status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['POST'])
def close_ticket(request, ticket_id: str):

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    solving_time = datetime.now(timezone.utc)
    ticket.solving_time = solving_time
    ticket.is_solved = True
    ticket.save()

    return Response(status=status.HTTP_200_OK)

# ------------------------- #

@api_view(http_method_names=['POST'])
def resume_ticket(request, ticket_id: str):

    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    resume_time = datetime.now(timezone.utc)
    in_pause = ticket.hours_in_pause
    delta = resume_time - ticket.last_pause_timestamp
    in_pause += delta.days * 24 + delta.seconds / 3600

    ticket.hours_in_pause = in_pause
    ticket.save()

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