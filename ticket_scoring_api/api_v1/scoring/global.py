from multiprocessing.sharedctypes import Value
import os
from turtle import clear
import yaml

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Callable, Any

from ticket_scoring_api.api_v1.models.static import *
from ticket_scoring_api.utils import dotdict

# ------------------------- #

# TODO: move all factories into separate file? e.g. ./factories.py

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

def _get_importance_calculator(ticket_type_id: int, **kwargs) -> Callable[..., float]:
    """
    Creation component for the importance score calculation factory.

    Args:
        ticket_type_id (int): ID match with ticket type string in static db table

    Raises:
        ValueError: unknown ID (i.e. unknown ticket type)

    Returns:
        Callable[..., float]: calculation function for specified ticket type
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
    return 90.0

# ------------------------- #

def _calc_importance_turnover_limit_alert(**kwargs) -> float:

    kwargs = dotdict(kwargs) #! unnecessary
    
    percentage = kwargs.limit_percentage
    amount = kwargs.limit_amount
    turnover30last = kwargs.turnover_last_thirty_days
    turnover30past = kwargs.turnover_past_thirty_days

    A1 = (100 - percentage) * amount / turnover30last
    A2 = (100 - percentage) * amount / turnover30past

    return 100. / max(0.75 * A1 + 0.25 * A2, 1)

# ------------------------- #

def _calc_importance_unverified_payment_source(**kwargs) -> float:
    return 110.0

# ------------------------- #

def _calc_importance_outgoing_account_payment(**kwargs) -> float:

    kwargs = dotdict(kwargs) #! unnecessary
    
    clearing_time = kwargs.clearing_time

    if clearing_time:
        now = datetime.now(timezone.utc)
        delta = clearing_time - now
        delta_hours = delta.days * 24 + delta.seconds / 3600

        return 100.0 * (1 - delta_hours / 120)
    
    else:
        return 105.0

# ------------------------- #

def _calc_importance_outgoing_account_payment_transfer(**kwargs) -> float:
    return _calc_importance_outgoing_account_payment(**kwargs)

# ------------------------- #