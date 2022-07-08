import logging
import os
import yaml

from numpy import ndarray
from pathlib import Path
from pmdarima import auto_arima
from typing import List

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)

with open(os.path.join(BASE_DIR, 'config/sarima_ET.yml'), 'r') as stream:
    default_config = yaml.load(stream, Loader=yaml.Loader)

# ------------------------- #

def forecast_expected_turnover(
        
        turnover_data: List[float],
        n_periods: int = 1, 
        default_config: dict = default_config, 
        **kwargs
        
    ) -> float:

    # * IndexError: too many indices for array: array is 0-dimensional, but 1 were indexed - can be caused by too high seaonality m term

    config = {**default_config, **kwargs}
    model = auto_arima(turnover_data, **config)
    forecast = model.predict(n_periods=n_periods)

    return float(forecast)
