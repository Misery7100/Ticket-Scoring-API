from rest_framework.serializers import ModelSerializer
from typing import Callable, Any, Dict

from api_v1.serializers import *
from api_v1.models.dynamic import *
from backend.local import *

from .utils import get_total_amount_eur

# ------------------------- #

def preprocess_ticket_data(data: Dict[str, Any], ticket_type: str) -> ModelSerializer:
    """
    Data preprocessing factory for different ticket types.

    Args:
        data (Dict[str, Any]): request data from @add_ticket API endpoint
        ticket_type (str): specified ticket type

    Returns:
        ModelSerializer: preprocessed and serialized data
    """

    preprocessor = _get_data_preprocessor(ticket_type)

    return preprocessor(data)

# ------------------------- #

def _get_data_preprocessor(ticket_type: str) -> Callable[..., ModelSerializer]:
    """
    Creation component for the data preprocessing factory.

    Args:
        ticket_type (str): specified ticket type

    Raises:
        ValueError: unknown ticket type

    Returns:
        Callable[[Dict[str, Any]], ModelSerializer]: preprocessing function for the specified ticket type
    """

    if ticket_type == 'verify_profile':
        return _preprocess_verify_profile
    
    elif ticket_type == 'turnover_limit_alert':
        return _preprocess_turnover_limit_alert
    
    elif ticket_type == 'unverified_payment_source':
        return _preprocess_unverified_payment_source
    
    elif ticket_type == 'outgoing_account_payment':
        return _preprocess_outgoing_account_payment
    
    elif ticket_type == 'outgoing_account_payment_transfer':
        return _preprocess_outgoing_account_payment_transfer
    
    else:
        raise ValueError(ticket_type)

# ------------------------- #

def _preprocess_verify_profile(data: Dict[str, Any]) -> VerifyProfileSerializer:
    """
    Data preprocessing and serialization implementation for "Verify profile"
    ticket type. 

    Args:
        data (Dict[str, Any]): request data from @add_ticket API endpoint

    Returns:
        VerifyProfileSerializer: preprocessed and serialized data
    """

    # involved brands
    if data.get('brands', False):

        for brand in data['brands']:
            brand['ticket_assigned'] = data['ticket_assigned']
            brand_data = BrandSerializer(data=brand)
            brand_data.is_valid(raise_exception=True) # raises 400 if invalid
            brand_data.save()
        
        brand_ids = [brand['brand_local_id'] for brand in data['brands']]
        data['brands'] = brand_ids
    
    return VerifyProfileSerializer(data=data)

# ......................... #

def _preprocess_turnover_limit_alert(data: Dict[str, Any]) -> TurnoverLimitAlertSerializer:
    """
    Data preprocessing and serialization implementation for "Turnover limit alert"
    ticket type.

    Args:
        data (Dict[str, Any]): request data from @add_ticket API endpoint

    Returns:
        TurnoverLimitAlertSerializer: preprocessed and serialized data
    """
    
    # track involved entities (we trackin it as arrays dude)
    if data.get('brands', False):
        pass

    if data.get('channels', False):
        pass

    if data.get('accounts', False):
        pass

    if data.get('terminals', False):
        pass

    if data.get('currencies', False):
        pass

    return TurnoverLimitAlertSerializer(data=data)

# ......................... #

def _preprocess_unverified_payment_source(data: Dict[str, Any]) -> UnverifiedPaymentSourceSerializer:
    """
    Data preprocessing and serialization implementation for "Unverified payment source"
    ticket type.

    Args:
        data (Dict[str, Any]): request data from @add_ticket API endpoint

    Returns:
        UnverifiedPaymentSourceSerializer: preprocessed and serialized data
    """

    data['payment_amount'] = get_total_amount_eur(data['amount'])
    
    return UnverifiedPaymentSourceSerializer(data=data)

# ......................... #

def _preprocess_outgoing_account_payment(data: Dict[str, Any]) -> OutgoingAccountPaymentSerializer:
    """
    Data preprocessing and serialization implementation for "Outgoing account payment"
    ticket type.

    Args:
        data (Dict[str, Any]): request data from @add_ticket API endpoint

    Returns:
        OutgoingAccountPaymentSerializer: preprocessed and serialized data
    """

    data['payment_amount'] = get_total_amount_eur(data['amount'])

    return OutgoingAccountPaymentSerializer(data=data)

# ......................... #

def _preprocess_outgoing_account_payment_transfer(data: Dict[str, Any]) -> OutgoingAccountPaymentTransferSerializer:
    """
    Data preprocessing and serialization implementation for "Outgoing account payment transfer"
    ticket type.

    Args:
        data (Dict[str, Any]): request data from @add_ticket API endpoint

    Returns:
        OutgoingAccountPaymentTransferSerializer: preprocessed and serialized data
    """

    data['payment_amount'] = get_total_amount_eur(data['amount'])

    return OutgoingAccountPaymentTransferSerializer(data=data)

# ------------------------- #