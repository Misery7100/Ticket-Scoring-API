import logging

from django.shortcuts import get_object_or_404
from django_celery_beat.models import PeriodicTask, PeriodicTasks, IntervalSchedule

from api_v1.models.dynamic import Ticket
from api_v1.models.static import TicketStatus, get_value_by_id
from api_v1.scoring.general import update_average_solving_time_all_ticket_types
from backend.celery import app as celery_app

# ------------------------- #

logger = logging.getLogger(__name__)

# ------------------------- #

@celery_app.task
def test(arg: str = 'test'):
    logger.warning(f'! {arg=} !')

# ------------------------- #

@celery_app.task
def report_status(ticket_id: str):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    status = ticket.ticket_status_id

    status_str = get_value_by_id(status, name='ticket_status')

    return f'"{ticket_id}" is {status_str}'

# ------------------------- #

@celery_app.task
def update_average_solving_time():
    values_types = update_average_solving_time_all_ticket_types()
    for value, type_ in values_types:
        ticket_type_name = get_value_by_id(type_, name='ticket_type')
        logger.info(f'new AVG time : "{ticket_type_name}" - {value:.2f} h ({(value * 60):.2f} min)')
    
# ------------------------- #
