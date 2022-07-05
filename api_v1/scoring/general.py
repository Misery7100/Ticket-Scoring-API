import logging
import os
import numpy as np
import yaml

from datetime import datetime, timezone
from dateutil import parser as dtparser
from pathlib import Path
from typing import Callable, List, Tuple

from api_v1.models.dynamic import *
from api_v1.models.static import *
from api_v1.scoring.forecast import forecast_expected_turnover
from api_v1.scoring.utils import sigmoid
from backend.local import staticdata
from backend.utils import dotdict

# ------------------------- #

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent

with open(os.path.join(BASE_DIR, 'config/importance.yml'), 'r') as stream:
    importance_cfg = dotdict(yaml.load(stream, Loader=yaml.Loader))

# ------------------------- #

def get_importance(ticket_type_id: int, **kwargs) -> float:
    """
    Importance score calculation factory for different ticket types.

    Args:
        ticket_type_id (int): ID match with ticket type string in static db table

    Returns:
        float: importance score
    """

    calculator = _get_importance_calculator(ticket_type_id=ticket_type_id)
    return calculator(**kwargs)

# ------------------------- #

def _get_importance_calculator(ticket_type_id: int) -> Callable[..., float]:
    """
    Creation component for the importance score calculation factory.

    Args:
        ticket_type_id (int): ID match with ticket type string in static db table

    Raises:
        ValueError: unknown ID (i.e. unknown ticket type)

    Returns:
        Callable[..., float]: calculation function for the specified ticket type
    """
    
    if ticket_type_id == get_id_by_value('verify_profile', name='ticket_type'):
        return _calc_importance_verify_profile
    
    elif ticket_type_id == get_id_by_value('outgoing_account_payment', name='ticket_type'):
        return _calc_importance_outgoing_account_payment
    
    elif ticket_type_id == get_id_by_value('outgoing_account_payment_transfer', name='ticket_type'):
        return _calc_importance_outgoing_account_payment_transfer

    elif ticket_type_id == get_id_by_value('unverified_payment_source', name='ticket_type'):
        return _calc_importance_unverified_payment_source
    
    elif ticket_type_id == get_id_by_value('turnover_limit_alert', name='ticket_type'):
        return _calc_importance_turnover_limit_alert
    
    else:
        raise ValueError(ticket_type_id)

# ------------------------- #

def _calc_importance_verify_profile(**kwargs) -> float:
    """
    The importance score calculation for "Verify profile" ticket type.

    Returns:
        float: importance score
    """

    return 90.0

# ------------------------- #

def _calc_importance_turnover_limit_alert(**kwargs) -> float:
    """
    The importance score calculation for "Turnover limit alert" ticket type.

    Returns:
        float: importance score
    """

    kwargs = dotdict(kwargs)
    
    percentage = kwargs.limit_percentage
    amount = kwargs.limit_amount
    turnover_history = kwargs.turnover_history
    issue_date = kwargs.limit_issue_date

    now = datetime.now(timezone.utc)
    delta = (now - issue_date).days

    rough_estimate = delta * (100 / percentage - 1)
    limit_remain = (100 - percentage) * amount

    # check scale:

    # 1. rough estimate ~ day
    if rough_estimate <= 7:
        expected_turnover = forecast_expected_turnover(turnover_data=turnover_history)
        turnover_rescale = expected_turnover / 7 * rough_estimate

    # 2. rough estimate ~ week
    elif rough_estimate < 29:
        expected_turnover = forecast_expected_turnover(turnover_data=turnover_history, n_periods=4)
        expected_turnover = sum(expected_turnover)
        turnover_rescale = expected_turnover / 28 * rough_estimate
    
    # 3. rough estimate ~ month
    else:
        turnover_history = np.array_split(np.array(turnover_history), 4)
        turnover_history = list(map(sum, turnover_history))
        expected_turnover = forecast_expected_turnover(turnover_data=turnover_history, m=3)
        turnover_rescale = expected_turnover / 30 * rough_estimate
    
    sigma = importance_cfg.turnover_limit_alert.sigma #! move to the db
    beta = importance_cfg.turnover_limit_alert.beta #! move to the db

    importance = sigmoid(sigma * (turnover_rescale / (beta * limit_remain) - 1))
    
    return 100 * importance

# ------------------------- #

def _calc_importance_unverified_payment_source(**kwargs) -> float:
    """
    The importance score calculation for "Unverified payment source" ticket type.

    Returns:
        float: importance score
    """

    return 110.0

# ------------------------- #

def _calc_importance_outgoing_account_payment(**kwargs) -> float:
    """
    The importance score calculation for "Outgoing account payment" ticket type.

    Returns:
        float: importance score
    """
    
    clearing_time = kwargs.get('clearing_time', False)

    if clearing_time:
        now = datetime.now(timezone.utc)
        delta = clearing_time - now
        delta_hours = delta.days * 24 + delta.seconds / 3600

        return 100.0 * (1 - delta_hours / 120)
    
    else:
        return 105.0

# ------------------------- #

def _calc_importance_outgoing_account_payment_transfer(**kwargs) -> float:
    """
    The importance score calculation for "Outgoing account payment transfer" ticket type.

    Returns:
        float: importance score
    """

    return _calc_importance_outgoing_account_payment(**kwargs)

# ------------------------- #

def get_internal_score(ticket_type_id: int, ticket_id: str, **kwargs) -> float:
    """
    Internal score calculation factory for different ticket types.

    Args:
        ticket_type_id (int): ID match with ticket type string in static db table

    Returns:
        float: importance score
    """

    calculator = _get_internal_score_calculator(ticket_type_id=ticket_type_id)
    return calculator(ticket_id, **kwargs)

# ------------------------- #

def _get_internal_score_calculator(ticket_type_id: int) -> Callable[..., float]:
    """
    Creation component for the internal score calculation factory.

    Args:
        ticket_type_id (int): ID match with ticket type string in static db table

    Raises:
        ValueError: unknown ID (i.e. unknown ticket type)

    Returns:
        Callable[..., float]: calculation function for the specified ticket type
    """
    
    if ticket_type_id == get_id_by_value('verify_profile', name='ticket_type'):
        return _calc_internal_score_verify_profile
    
    elif ticket_type_id == get_id_by_value('outgoing_account_payment', name='ticket_type'):
        return _calc_internal_score_outgoing_account_payment
    
    elif ticket_type_id == get_id_by_value('outgoing_account_payment_transfer', name='ticket_type'):
        return _calc_internal_score_outgoing_account_payment_transfer

    elif ticket_type_id == get_id_by_value('unverified_payment_source', name='ticket_type'):
        return _calc_internal_score_unverified_payment_source
    
    elif ticket_type_id == get_id_by_value('turnover_limit_alert', name='ticket_type'):
        return _calc_internal_score_turnover_limit_alert
    
    else:
        raise ValueError(ticket_type_id)

# ------------------------- #

def _get_or_update_max_relative_score(ticket_type: str, score: float) -> float:

    rel_score = MaxRelativeScore.objects.get(ticket_type_id=get_id_by_value(ticket_type, name='ticket_type'))

    if rel_score.max_relative_score < score:
        rel_score.max_relative_score = score
        rel_score.save()

    return rel_score.max_relative_score

# ------------------------- #

def _calc_internal_score_verify_profile(ticket_id: str, **kwargs) -> float:
    """
    The internal score calculation for "Verify profile" ticket type.

    Args:
        ticket_id (str): ticket ID in the universal format

    Returns:
        float: internal score
    """

    score = 0
    trust_score = 1 # TODO: trust scoring based on historical data
    period = kwargs.get('period', 1)

    for brand in Brand.objects.filter(ticket_assigned=ticket_id):
        score += float(brand.specified_turnover_current) * brand.average_fee_rate * period * trust_score
    
    max_rel_score = _get_or_update_max_relative_score('verify_profile', score)
    internal_score = (score / max_rel_score) ** 0.3 #! need to verify

    return internal_score

# ------------------------- #

def _calc_internal_score_outgoing_account_payment(ticket_id: str, **kwargs) -> float:
    """
    The internal score calculation for "Outgoing account payment" ticket type.

    Args:
        ticket_id (str): ticket ID in the universal format

    Returns:
        float: internal score
    """

    ticket = OutgoingAccountPayment.objects.get(ticket_assigned=ticket_id)
    score = ticket.payment_amount

    max_rel_score = _get_or_update_max_relative_score('outgoing_account_payment', score)
    internal_score = (score / max_rel_score) ** 0.3

    return internal_score

# ------------------------- #

def _calc_internal_score_outgoing_account_payment_transfer(ticket_id: str, **kwargs) -> float:
    """
    The internal score calculation for "Outgoing account payment transfer" ticket type.

    Args:
        ticket_id (str): ticket ID in the universal format

    Returns:
        float: internal score
    """

    ticket = OutgoingAccountPaymentTransfer.objects.get(ticket_assigned=ticket_id)
    score = ticket.payment_amount

    max_rel_score = _get_or_update_max_relative_score('outgoing_account_payment_transfer', score)
    internal_score = (score / max_rel_score) ** 0.3

    return internal_score

# ------------------------- #

def _calc_internal_score_unverified_payment_source(ticket_id: str, **kwargs) -> float:
    """
    The internal score calculation for "Unverified payment source" ticket type.

    Args:
        ticket_id (str): ticket ID in the universal format

    Returns:
        float: internal score
    """

    ticket = UnverifiedPaymentSource.objects.get(ticket_assigned=ticket_id)
    score = ticket.payment_amount

    max_rel_score = _get_or_update_max_relative_score('unverified_payment_source', score)
    internal_score = 1 + (score / max_rel_score)

    return internal_score

# ------------------------- #

def _calc_internal_score_turnover_limit_alert(ticket_id: str, **kwargs) -> float:
    """
    The internal score calculation for "Turnover limit alret" ticket type.

    Args:
        ticket_id (str): ticket ID in the universal format

    Returns:
        float: internal score
    """

    internal_score = 1

    return internal_score

# ------------------------- #

def _update_and_get_average_solving_time(ticket_type_id: int) -> float:

    avg_sol_time = AverageSolvingTime.objects.get(ticket_type_id=ticket_type_id)
    solving_times = []

    for ticket in Ticket.objects.filter(
            ticket_status_id=get_id_by_value('closed', name='ticket_status'),
            ticket_type_id=ticket_type_id
        ):
        
        delta = ticket.solving_date - ticket.issue_date
        hours_to_solve = delta.days * 24 + delta.seconds / 3600
        hours_to_solve -= ticket.hours_in_pause
        solving_times.append(hours_to_solve)
    
    if solving_times:
        new_avg_sol_time = sum(solving_times) / len(solving_times)
        avg_sol_time.avg_solving_time_hours = new_avg_sol_time
        avg_sol_time.save()

    return avg_sol_time.avg_solving_time_hours

# ------------------------- #

def update_average_solving_time_all_ticket_types() -> List[Tuple[float, int]]:

    values_types = []
    
    for ticket_type_id in staticdata['ticket_type'].values():
        value = _update_and_get_average_solving_time(ticket_type_id=ticket_type_id)
        values_types.append((value, ticket_type_id))
    
    return values_types

# ------------------------- #
# TODO: replace with normalized estimation of solving time (further, v2)
def get_normalized_average_solving_time(ticket_type_id: int) -> float:

    if ticket_type_id == get_id_by_value('unverified_payment_source', name='ticket_type'):
        return 1
    
    else:
        numerator = 0
        denominator = 0

        for obj in AverageSolvingTime.objects.all():

            if obj.ticket_type_id == ticket_type_id:
                numerator = obj.avg_solving_time_hours

            denominator += obj.avg_solving_time_hours

        # not so high impact for numerator << denominator
        return 1 - (numerator / denominator) ** 3

# ------------------------- #

def get_ticket_type_score(ticket_type_id: int, **kwargs) -> float:

    importance = get_importance(ticket_type_id=ticket_type_id, **kwargs)
    ast_norm = get_normalized_average_solving_time(ticket_type_id=ticket_type_id)

    return importance * ast_norm

# ------------------------- #

def get_general_score(ticket_type_id: int, ticket_id: str, **kwargs) -> float:

    ticket_type_score = get_ticket_type_score(ticket_type_id=ticket_type_id, **kwargs)
    internal_score = get_internal_score(ticket_type_id=ticket_type_id, ticket_id=ticket_id, **kwargs)

    return ticket_type_score * internal_score

# ------------------------- #