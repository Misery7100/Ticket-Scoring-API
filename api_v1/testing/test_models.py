import uuid

from django.test import TestCase

from api_v1.testing.factories import *

# ------------------------------ #

class Ticket(TestCase):

    def test_str(self):
        ticket = TicketFactory()
        print('\n', ticket)
        self.assertEqual(str(ticket), f'{ticket.ticket_id} at {ticket.server_id}')
        self.assertEqual(len(ticket.ticket_id), len(str(uuid.uuid4())))