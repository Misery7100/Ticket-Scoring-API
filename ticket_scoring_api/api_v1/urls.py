from django.urls import include, re_path, path
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet

# ------------------------- #

router = DefaultRouter()
router.register(r'ticket', TicketViewSet, basename='ticket')

urlpatterns = [
    re_path('^', include(router.urls)),
]

print(urlpatterns)