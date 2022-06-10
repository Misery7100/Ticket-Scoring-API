from rest_framework.serializers import ModelSerializer
from .models import *

# ------------------------- #

class VerifyProfileSerializer(ModelSerializer):

    class Meta:
        model = VerifyProfileData
        fields = '__all__'