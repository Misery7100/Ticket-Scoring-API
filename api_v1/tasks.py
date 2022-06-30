import logging

from datetime import datetime, timezone

from api_v1.models.static import get_value_by_id
from api_v1.scoring.general import update_average_solving_time_all_ticket_types, get_general_score
from api_v1.serializers import ScoringGlobalSerializer
from backend.celery import app as celery_app

# ------------------------- #

logger = logging.getLogger(__name__)

# ------------------------- #

@celery_app.task
def update_ticket_score(ticket_type_id: int, ticket_id: str, **kwargs) -> float:
    score = get_general_score(ticket_id=ticket_id, ticket_type_id=ticket_type_id, **kwargs)
    now = datetime.now(timezone.utc)
    
    data = dict(
        ticket_assigned=ticket_id,
        score=score,
        timestamp=now
    )

    record = ScoringGlobalSerializer(data=data)
    record.is_valid(raise_exception=True)
    record.save()

    # TODO: push the result to external endpoint async

    return score

# ------------------------- #

@celery_app.task
def update_average_solving_time():
    values_types = update_average_solving_time_all_ticket_types()
    for value, type_ in values_types:
        ticket_type_name = get_value_by_id(type_, name='ticket_type')
        logger.info(f'new AVG time : "{ticket_type_name}" - {value:.2f} h ({(value * 60):.2f} min)')
    
# ------------------------- #
