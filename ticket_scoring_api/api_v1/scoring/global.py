import os
from turtle import clear
import yaml

from pathlib import Path
from datetime import datetime, timezone
from ticket_scoring_api.api_v1.static_models import *

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent #! ah shit dude

with open(os.path.join(BASE_DIR, 'secret/staticdata.yml'), 'r') as stream:
    staticdata = yaml.safe_load(stream)

# ------------------------- #

def importance(ticket_type_id: int, **kwargs) -> float:

    # TODO: handle list, vectorize for the same ticket type

    if ticket_type_id == get_id_by_value('verify_profile', name='ticket_type'):
        return 90.
    
    elif ticket_type_id == get_id_by_value('outgoing_account_payment', name='ticket_type') or \
         ticket_type_id == get_id_by_value('outgoing_account_payment_transfer', name='ticket_type'):

        clearing_time = kwargs['clearing_time']

        if clearing_time:
            now = datetime.now(timezone.utc)
            delta = clearing_time - now
            delta_hours = delta.days * 24 + delta.seconds / 3600

            return 100. * (1 - delta_hours / 120)
        
        else:
            return 105.
    
    elif ticket_type_id == get_id_by_value('unverified_payment_source', name='ticket_type'):
        return 110.
    
    elif ticket_type_id == get_id_by_value('turnover_limit_alert', name='ticket_type'):
        percentage = kwargs['limit_percentage']
        amount = kwargs['limit_amount']
        turnover30last = kwargs['turnover_last_thirty_days']
        turnover30past = kwargs['turnover_past_thirty_days']

        A1 = (100 - percentage) * amount / turnover30last
        A2 = (100 - percentage) * amount / turnover30past

        return 100. / max(0.75 * A1 + 0.25 * A2, 1)
    
    else:

        raise ValueError(f'unknown {ticket_type_id=}')

# ------------------------- #
