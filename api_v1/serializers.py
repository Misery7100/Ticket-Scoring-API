from rest_framework.serializers import ModelSerializer

from ticket_scoring_api.utils import dotdict

from .models.dynamic import *

# ------------------------- #

class TicketSerializer(ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            'ticket_id',
            'ticket_type_id',
            'server_id',
            'client_id',
            'issue_date',
            'solving_date',
            'ticket_status_id',
            'hours_in_pause',
            'last_pause_timestamp'
        )

# ------------------------- #

class VerifyProfileSerializer(ModelSerializer):
    class Meta:
        model = VerifyProfile
        fields = '__all__'

# ------------------------- #

class TurnoverLimitAlertSerializer(ModelSerializer):
    class Meta:
        model = TurnoverLimitAlert
        fields = ('__all__')

# ------------------------- #

class UnverifiedPaymentSourceSerializer(ModelSerializer):
    class Meta:
        model = UnverifiedPaymentSource
        fields = '__all__'

# ------------------------- #

class OutgoingAccountPaymentSerializer(ModelSerializer):
    class Meta:
        model = OutgoingAccountPayment
        fields = '__all__'

# ------------------------- #

class OutgoingAccountPaymentTransferSerializer(ModelSerializer):
    class Meta:
        model = OutgoingAccountPaymentTransfer
        fields = '__all__'

# ------------------------- #