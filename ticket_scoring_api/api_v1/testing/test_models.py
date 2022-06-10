from django.test import TestCase

from .factories import *

# ------------------------------ #

class BaseTicketCase(TestCase):

    def test_str(self):

        ticket = BaseTicketFactory()
        self.assertEqual(str(ticket), f'{ticket.ticket_id} at {ticket.server_id}')