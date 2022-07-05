from django.contrib.postgres import fields as psqlfields
from django.db import models

# ------------------------- #

class Ticket(models.Model):

    ticket_id = models.CharField(max_length=100, primary_key=True)
    ticket_type_id = models.SmallIntegerField(default=1)
    server_id = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    issue_date = models.DateTimeField()
    solving_date = models.DateTimeField(blank=True, null=True)
    ticket_status_id = models.SmallIntegerField(default=1)
    hours_in_pause = models.FloatField(default=0.0, blank=True, null=True)
    last_pause_timestamp = models.DateTimeField(blank=True, null=True)
    
    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_ticket_global'

# ------------------------- #

class VerifyProfile(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, primary_key=True, on_delete=models.CASCADE)
    scoring_type = models.CharField(max_length=100)
    account_type = models.CharField(max_length=100)
    legal_country_code = models.CharField(max_length=20)
    legal_entity_type = models.CharField(max_length=50, blank=True, null=True)
    profile_bank_accounts = models.IntegerField(default=0)
    enabled_currencies = psqlfields.ArrayField(models.CharField(max_length=10), blank=True, null=True)
    brands = psqlfields.ArrayField(models.CharField(max_length=100), blank=True, null=True, default=list)

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_verify_profile'

# ------------------------- #

class Brand(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    brand_local_id = models.CharField(max_length=100)
    average_fee_rate = models.FloatField()
    account_category_type = models.IntegerField()
    specified_turnover_current = models.FloatField(blank=True, null=True)
    specified_turnover_in_3_m = models.FloatField(blank=True, null=True)
    specified_turnover_in_6_m = models.FloatField(blank=True, null=True)
    specified_turnover_in_12_m = models.FloatField(blank=True, null=True)
    
    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_brand_verify_profile'

# ------------------------- #

class UnverifiedPaymentSource(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, primary_key=True, on_delete=models.CASCADE)
    payment_amount = models.FloatField()
    currencies = psqlfields.ArrayField(models.CharField(max_length=10), blank=True, null=True)

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_unverified_payment_source'

# ------------------------- #

class TurnoverLimitAlert(models.Model):

    # main comps (?)
    ticket_assigned = models.OneToOneField(Ticket, primary_key=True, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=100)
    legal_country_code = models.CharField(max_length=20)
    legal_entity_type = models.CharField(max_length=50, blank=True, null=True)

    limit_type = models.CharField(max_length=50)
    limit_product = models.CharField(max_length=50)
    limit_entity = models.CharField(max_length=50)
    limit_percentage = models.FloatField()
    limit_amount = models.FloatField()
    limit_issue_date = models.DateTimeField()

    turnover_history = psqlfields.ArrayField(models.FloatField(), blank=True, default=list) # in EUR

    # just to trace statistics
    brands = psqlfields.ArrayField(models.CharField(max_length=100), blank=True, null=True, default=list)
    channels = psqlfields.ArrayField(models.CharField(max_length=100), blank=True, null=True, default=list)
    terminals = psqlfields.ArrayField(models.CharField(max_length=100), blank=True, null=True, default=list)
    currencies = psqlfields.ArrayField(models.CharField(max_length=100), blank=True, null=True, default=list)

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_turnover_limit_alert'

# ------------------------- #

class OutgoingAccountPayment(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, primary_key=True, on_delete=models.CASCADE)
    payment_amount = models.FloatField()
    clearing_time = models.DateTimeField(blank=True, null=True)

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_outgoing_account_payment'

# ------------------------- #

class OutgoingAccountPaymentTransfer(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, primary_key=True, on_delete=models.CASCADE)
    payment_amount = models.FloatField()
    clearing_time = models.DateTimeField(blank=True)

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_outgoing_account_payment_transfer'

# ------------------------- #

class ScoringGlobal(models.Model):

    ticket_assigned = models.ForeignKey(Ticket, primary_key=False, on_delete=models.CASCADE)
    score = models.FloatField()
    timestamp = models.DateTimeField()

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_scoring_global'

# ------------------------- #

class AverageSolvingTime(models.Model):

    ticket_type_id = models.SmallIntegerField()
    avg_solving_time_hours = models.FloatField()

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_average_solving_time'

# ------------------------- #

class MaxRelativeScore(models.Model):

    ticket_type_id = models.SmallIntegerField()
    max_relative_score = models.FloatField()

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_maximum_relative_score'

# ------------------------- #

# TODO: models for ML
# TODO: models for storage optimization (?)