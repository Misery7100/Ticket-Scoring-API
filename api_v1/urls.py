from django.urls import include, path
from .endpoints import ticket_actions

# ------------------------- #

urlpatterns = [
    path('add-ticket', ticket_actions.add_ticket, name='add-ticket'),
    path('get-ticket/<str:ticket_id>', ticket_actions.get_ticket, name='get-ticket'),
    path('delete-ticket/<str:ticket_id>', ticket_actions.delete_ticket, name='delete-ticket'),
    path('pause-ticket/<str:ticket_id>', ticket_actions.pause_ticket, name='pause-ticket'),
    path('resume-ticket/<str:ticket_id>', ticket_actions.resume_ticket, name='resume-ticket'),
    path('close-ticket/<str:ticket_id>', ticket_actions.close_ticket, name='close-ticket'),
]