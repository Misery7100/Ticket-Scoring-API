from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *

# ------------------------- #

class TicketViewSet(GenericViewSet,  # generic view functionality
                 CreateModelMixin,  # handles POSTs
                 RetrieveModelMixin,  # handles GETs for 1 object
                 UpdateModelMixin,  # handles PUTs and PATCHes
                 ListModelMixin):  # handles GETs for many objects
    
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()

    # ......................... #

    @action(methods=['post'])
    def pause_ticket(self, request, pk):
        pass

    # ......................... #

    @action(methods=['post'])
    def resume_ticket(self, request, pk):
        pass

    # ......................... #

# ------------------------- #

class VerifyProfileViewSet(TicketViewSet):

    serializer_class = VerifyProfileSerializer
    queryset = VerifyProfile.objects.all()

    # ......................... #

    def create(self, request, **kwargs):
        super().create(request, **kwargs)

        # ...
    
    # ......................... #

    def update(self, request, **kwargs):
        super().update(request, **kwargs)

        # ...

# ------------------------- #

class TurnoverLimitAlertViewSet(TicketViewSet):

    serializer_class = TurnoverLimitAlertSerializer
    queryset = TurnoverLimitAlert.objects.all()

    # ......................... #

    def create(self, request, **kwargs):
        super().create(request, **kwargs)

        # ...
    
    # ......................... #
    
    def update(self, request, **kwargs):
        super().update(request, **kwargs)

        # ...

# ------------------------- #

class UnverifiedPaymentSourceViewSet(TicketViewSet):

    serializer_class = UnverifiedPaymentSourceSerializer
    queryset = UnverifiedPaymentSource.objects.all()

    # ......................... #

    def create(self, request, **kwargs):
        super().create(request, **kwargs)

        # ...

    # ......................... #
    
    def update(self, request, **kwargs):
        super().update(request, **kwargs)

        # ...

# ------------------------- #

class OutgoingAccountPaymentViewSet(TicketViewSet):

    serializer_class = OutgoingAccountPaymentSerializer
    queryset = OutgoingAccountPayment.objects.all()

    # ......................... #

    def create(self, request, **kwargs):
        super().create(request, **kwargs)

        # ...
    
    # ......................... #
    
    def update(self, request, **kwargs):
        super().update(request, **kwargs)

        # ...

# ------------------------- #

class OutgoingAccountPaymentTransferViewSet(TicketViewSet):

    serializer_class = OutgoingAccountPaymentTransferSerializer
    queryset = OutgoingAccountPaymentTransfer.objects.all()

    # ......................... #

    def create(self, request, **kwargs):
        super().create(request, **kwargs)

        # ...
    
    # ......................... #
    
    def update(self, request, **kwargs):
        super().update(request, **kwargs)

        # ...