from datetime import datetime, timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from ticket_scoring_api.api_v1.models.dynamic import *
from ticket_scoring_api.api_v1.serializers import *

# ------------------------- #

@api_view(http_method_names=['GET'])
def get_current_status(request):
    pass

# ------------------------- #

@api_view(http_method_names=['POST'])
def update_configuration(request):
    pass

# ------------------------- #

@api_view(http_method_names=['POST'])
def force_ml_stuff_retrain(request):
    pass

# ------------------------- #