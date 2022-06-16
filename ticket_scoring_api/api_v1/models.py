from django.db import models
from django.contrib.postgres import fields as psqlfields

# ------------------------- #

class Ticket(models.Model):

    """General ticket storage
    """

    ticket_id = models.CharField(max_length=100, primary_key=True)
    ticket_type = models.CharField(max_length=100)
    server_id = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    issue_date = models.DateTimeField(max_length=50)
    solving_date = models.DateTimeField(max_length=50, blank=True, null=True)
    is_solved = models.BooleanField(default=False, blank=True, null=True)
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
    brands = psqlfields.ArrayField(models.CharField(max_length=100), blank=True, null=True)

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
        db_table = 'history"."api_v1_verify_profile_brand'

# ------------------------- #

class UnverifiedPaymentSource(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, primary_key=True, on_delete=models.CASCADE)
    amount = models.FloatField()
    currencies = psqlfields.ArrayField(models.CharField(max_length=10), blank=True, null=True)

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_unverified_payment_source'

# ------------------------- #

class TurnoverLimitAlert(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, primary_key=True, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=100)
    legal_country_code = models.CharField(max_length=20)
    legal_entity_type = models.CharField(max_length=50, blank=True, null=True)

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_turnover_limit_alert'

# ------------------------- #

class OutgoingAccountPayment(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, primary_key=True, on_delete=models.CASCADE)
    amount = models.FloatField()
    clearing_time = models.DateTimeField(blank=True, null=True)

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_outgoing_account_payment'

# ------------------------- #

class OutgoingAccountPaymentTransfer(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, primary_key=True, on_delete=models.CASCADE)
    amount = models.FloatField()
    clearing_time = models.DateTimeField(blank=True)

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_outgoing_account_payment_transfer'

# ------------------------- #

class ScoringGlobal(models.Model):

    ticket_assigned = models.OneToOneField(Ticket, primary_key=False, on_delete=models.CASCADE)
    score = models.FloatField()
    timestamp = models.DateTimeField()

    # ......................... #

    class Meta:
        db_table = 'history"."api_v1_scoring_global'

# ------------------------- #

# TODO: models for ML

# ------------------------- #

# MODELS = {
#     'verify_profile' : VerifyProfile,
#     'turnover_limit_alert' : TurnoverLimitAlert,
#     'unverified_payment_source' : UnverifiedPaymentSource,
#     'outgoing_account_payment' : OutgoingAccountPayment,
#     'outgoing_account_payment_transfer' : OutgoingAccountPaymentTransfer
# }

# # ------------------------- #