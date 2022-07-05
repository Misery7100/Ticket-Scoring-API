import numpy as np
import requests

from typing import Dict, List

from backend.local import *
from backend.utils import dotdict

# ------------------------- #

def get_total_amount_eur(amount_dict: Dict[str, float]) -> float:

    amount = 0

    # calculate total transfer amount in EUR
    for currency, value in amount_dict.items():
        amount += convert_currency_to_eur(value, currency)
    
    return amount

# ------------------------- #

def convert_currency_to_eur(

        amount: float, 
        currency: str, 
        credentials: dotdict = credentials

    ) -> float:

    creds = credentials.alphavantage
    url = f'{creds.url}&from_currency={currency}&to_currency=EUR&apikey={creds.api_key}'
    res = requests.get(url)
    result = res.json()

    exchange_rate = float(result['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    converted = amount * exchange_rate

    return converted

# ------------------------- #

def get_mom_growth_perc(month2: float, month1: float) -> float:
    """
    Calculate Month-over-Month growth rate.

    Args:
        month2 (float): monthly metric
        month1 (float): previous monthly metric

    Returns:
        float: MoM growth rate
    """

    return (month2 - month1) / month1

# ------------------------- #

def get_mom_growth_average(months: List[float]) -> float:
    """
    Calculate average Month-over-Month growth rate.

    Args:
        months (List[float]): monthly metrics sorted chronologically.

    Returns:
        float: average MoM growth rate
    """

    assert(len(months) > 0)
    
    momgps = [
        get_mom_growth_perc(months[i + 1], months[i])
        for i in range(len(months) - 1)
    ]

    return sum(momgps) / len(momgps)

# ------------------------- #

def get_compound_growth_rate(last_period: float, first_period: float, period_difference: int) -> float:
    """
    Calculate compound growth rate.

    Args:
        last_month (float): last period metric
        first_month (float): first period metric
        period_difference (int): time difference between last and first period in periods

    Returns:
        float: CMGR
    """

    assert (period_difference > 0)

    return (last_period / first_period) ** (1 / period_difference) - 1

# ------------------------- #

def sigmoid(x):
    return 1 / (1 + np.exp(-x))