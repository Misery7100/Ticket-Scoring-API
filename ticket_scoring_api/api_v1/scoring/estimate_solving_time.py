from ticket_scoring_api.api_v1.models import *

# ------------------------- #

def update_avg_solving_time(period: int):
    pass

    # TODO: make it async (with celery (?))

    # get all closed tickets within specified period
    # ...

    # calculate avg hours to solve for different ticket types
    # ...

    # update db values
    # ...