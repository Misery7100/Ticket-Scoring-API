from factory import Faker
from factory.django import DjangoModelFactory

from api_v1.models.dynamic import *

# ------------------------- #

class TicketFactory(DjangoModelFactory):

    ticket_id = Faker('uuid4')
    server_id = Faker('uuid4')
    client_id = Faker('uuid4')
    ticket_issue_date = Faker('date_time')

    class Meta:
        model = Ticket

# ------------------------- #

class BrandFactory(DjangoModelFactory):

    class Meta:
        model = Brand