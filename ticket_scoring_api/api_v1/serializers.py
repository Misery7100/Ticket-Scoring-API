from rest_framework.serializers import ModelSerializer
from .models import *

# ------------------------- #

class TicketSerializer(ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

# ------------------------- #

class VerifyProfileSerializer(ModelSerializer):
    class Meta:
        model = VerifyProfile
        fields = '__all__'

# ------------------------- #

class TurnoverLimitAlertSerializer(ModelSerializer):
    class Meta:
        model = TurnoverLimitAlert
        fields = '__all__'

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