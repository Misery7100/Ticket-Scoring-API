from api_v1.models.dynamic import *

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