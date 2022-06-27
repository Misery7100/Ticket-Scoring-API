import requests
from typing import Callable, Any, Dict

from ticket_scoring_api.local import *
from ticket_scoring_api.utils import dotdict

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