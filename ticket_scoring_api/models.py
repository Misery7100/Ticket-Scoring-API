from django.db import models
from django.contrib.postgres import fields as psqlfields

# ------------------------- #

class BrandData(models.Model):

    ticket_id = models.CharField(max_length=100)
    brand_local_id = models.CharField(max_length=100)
    average_fee_rate = models.DecimalField()
    account_category_type = models.IntegerField()
    specified_turnover_current = models.DecimalField(blank=True)
    specified_turnover_in_3_m = models.DecimalField(blank=True)
    specified_turnover_in_6_m = models.DecimalField(blank=True)
    specified_turnover_in_12_m = models.DecimalField(blank=True)

    def __str__(self):
        return f'{self.brand_local_id} from {self.ticket_id}'

# ------------------------- #

class BaseTicketData(models.Model):

    ticket_id = models.CharField(max_length=100)
    server_id = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    ticket_issue_date = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.ticket_id} at {self.server_id}'

# ------------------------- #

class VerifyProfileData(BaseTicketData):

    scoring_type = models.CharField(max_length=100)
    account_type = models.CharField(max_length=100)
    legal_country_code = models.CharField(max_length=20)
    legal_entity_type = models.CharField(max_length=50, blank=True)
    profile_bank_accounts = models.IntegerField()
    enabled_currencies = psqlfields.ArrayField(models.CharField(max_length=10), blank=True)

# ------------------------- #
#? do we need it at all?
class UnverifiedPaySourceData(BaseTicketData):

    amount = models.DecimalField()

# ------------------------- #

class TurnoverLimitAlertData(BaseTicketData):

    amount = models.DecimalField()

# ------------------------- #