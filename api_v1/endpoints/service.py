from rest_framework.decorators import api_view

from api_v1.models.dynamic import *
from api_v1.serializers import *

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