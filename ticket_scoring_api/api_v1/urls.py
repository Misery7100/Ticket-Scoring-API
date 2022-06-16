from django.urls import include, path
from .endpoints import *

# ------------------------- #

urlpatterns = [
    path('add-ticket', add_ticket, name='add-ticket'),
    path('get-ticket/<str:ticket_id>', get_ticket, name='get-ticket'),
    #path('delete-ticket/<str:ticket_id>', delete_ticket, name='delete-ticket'),
    path('pause-ticket/<str:ticket_id>', pause_ticket, name='pause-ticket'),
    path('resume-ticket/<str:ticket_id>', resume_ticket, name='resume-ticket'),
    path('close-ticket/<str:ticket_id>', close_ticket, name='close-ticket'),
]