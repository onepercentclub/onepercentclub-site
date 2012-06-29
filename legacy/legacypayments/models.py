from django.db import models


class PaymentCluster(models.Model):
    # It's unique, but it's not the PK? I am confused...
    id = models.IntegerField(unique=True)
    order_id = models.IntegerField(primary_key=True)
    payment_cluster_id = models.BigIntegerField()
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    to_safe = models.DateTimeField(null=True, blank=True)
    payment_cluster_process = models.CharField(max_length=64)
    last_partial_payment_process = models.CharField(max_length=32, blank=True)
    last_partial_payment_method = models.CharField(max_length=128, blank=True)
    last_partial_payment_method_readable = models.CharField(
        max_length=128, blank=True
    )
    transaction_amount = models.DecimalField(max_digits=18, decimal_places=2)
    transaction_currency = models.CharField(max_length=16)
    used_payment_profile = models.CharField(max_length=255, blank=True)
    receipt_statement = models.CharField(max_length=256, blank=True)
    days_pay_period = models.CharField(max_length=32, blank=True)
    days_exhortation1 = models.CharField(max_length=255, blank=True)
    days_exhortation2 = models.CharField(max_length=255, blank=True)
    meta_amount_received = models.CharField(max_length=32)
    meta_considered_safe = models.CharField(max_length=8)
    meta_charged_back = models.CharField(max_length=8)
    payment_cluster_key = models.CharField(max_length=255, blank=True)
    payout_process = models.CharField(max_length=32, blank=True)
    client = models.ForeignKey('legacymembers.Member', null=True, blank=True)
    client_firstname = models.CharField(max_length=255, blank=True)
    client_lastname = models.CharField(max_length=255, blank=True)
    client_address = models.CharField(max_length=255, blank=True)
    client_zip = models.CharField(max_length=255, blank=True)
    client_city = models.CharField(max_length=255, blank=True)
    client_country = models.CharField(max_length=255, blank=True)
    client_language = models.CharField(max_length=255, blank=True)
    client_email = models.CharField(max_length=255, blank=True)
    include_costs = models.CharField(max_length=255, blank=True)
    profile_exhortation1 = models.CharField(max_length=255, blank=True)
    profile_exhortation2 = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'pay_payment_clusters'
        managed = False

    def fullname(self):
        return self.client_firstname + ' ' + self.client_lastname

    def method(self):
        return self.last_partial_payment_method

    def donation(self):
        if self.donation_set.count():
            return self.donation_set.all()[0]
        return None


class BankStatement(models.Model):
    id = models.IntegerField(primary_key=True)
    processed_date = models.DateTimeField()
    status = models.CharField(max_length=10)
    first_mutation = models.DateTimeField(null=True, blank=True)
    last_mutation = models.DateTimeField(null=True, blank=True)
    begin_balance = models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)
    end_balance = models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)

    class Meta:
        db_table = u'pay_bank_statements'
        managed = False


class BankStatementLine(models.Model):
    id = models.IntegerField(primary_key=True)
    bank_statement = models.ForeignKey(BankStatement)
    account_number = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    mutation_date = models.DateTimeField()
    status = models.CharField(max_length=10)
    type = models.CharField(max_length=12, blank=True)
    item_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = u'pay_bank_statement_lines'
        managed = False


class RequestLog(models.Model):
    id = models.IntegerField(primary_key=True)
    message = models.CharField(max_length=255, blank=True)
    file = models.CharField(max_length=255, blank=True)
    line = models.CharField(max_length=255, blank=True)
    client_ip = models.CharField(max_length=255, blank=True)
    request_url = models.CharField(max_length=255, blank=True)
    request_post = models.CharField(max_length=255, blank=True)
    error_code = models.CharField(max_length=255, blank=True)
    order_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = u'pay_request_log'
        managed = False


class Payment(models.Model):
    id = models.BigIntegerField(primary_key=True)
    payment_cluster = models.ForeignKey(PaymentCluster,
        db_column="payment_cluster_order_id"
    )
    created = models.DateTimeField()
    modified = models.DateTimeField()
    method = models.CharField(max_length=128, blank=True)
    method_readable = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=64)
    reason = models.TextField(blank=True)
    ucaf = models.CharField(max_length=8)
    visa_3ds = models.CharField(max_length=8)
    mcsc = models.CharField(max_length=255)
    vbv = models.CharField(max_length=255)
    issuer_id = models.CharField(max_length=255, blank=True)
    authorisation_id = models.CharField(max_length=255, blank=True)
    timestamp_authorisation = models.CharField(max_length=255, blank=True)
    bincountry = models.CharField(max_length=255, blank=True)
    member_code = models.CharField(max_length=255, blank=True)
    refund_member_code = models.CharField(max_length=255, blank=True)
    refund_batch_id = models.CharField(max_length=255, blank=True)
    refund_communication_id = models.CharField(max_length=255, blank=True)
    capture_batch_id = models.CharField(max_length=255, blank=True)
    capture_communication_id = models.CharField(max_length=255, blank=True)
    capture_authorisation_id = models.CharField(max_length=255, blank=True)
    capture_return_reference_id = models.CharField(max_length=255, blank=True)
    return_reference_id = models.CharField(max_length=255, blank=True)
    transaction_reference_nr = models.CharField(max_length=255, blank=True)
    communication_id = models.CharField(max_length=255, blank=True)
    payvision_payment_id = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'pay_payments'
        managed = False


class PaymentMethod(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    cost_variable = models.DecimalField(max_digits=5, decimal_places=2)
    cost_fixed = models.DecimalField(max_digits=12, decimal_places=2)
    cost_minimum = models.DecimalField(max_digits=12, decimal_places=2)
    cost_maximum = models.DecimalField(max_digits=12, decimal_places=2)
    chargeback_period = models.TextField() # This field type is a guess.

    class Meta:
        db_table = u'pay_payment_methods'
        managed = False


class Log(models.Model):
    id = models.IntegerField(primary_key=True)
    message = models.CharField(max_length=255, blank=True)
    file = models.CharField(max_length=255, blank=True)
    line = models.CharField(max_length=255, blank=True)
    client_ip = models.CharField(max_length=255, blank=True)
    client_id = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    order_id = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'pay_log'
        managed = False


class PaymentStateTransition(models.Model):
    id = models.IntegerField(primary_key=True)
    payment = models.ForeignKey(Payment, null=True, blank=True)
    from_state = models.CharField(max_length=64, blank=True)
    to_state = models.CharField(max_length=64, blank=True)
    reason = models.TextField(blank=True)
    date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'pay_payment_state_transitions'
        managed = False


class PaymentClusterStateTransition(models.Model):
    id = models.IntegerField(primary_key=True)
    payment_cluster = models.ForeignKey(PaymentCluster,
        max_length=255, blank=True
    )
    from_state = models.CharField(max_length=64, blank=True)
    to_state = models.CharField(max_length=64, blank=True)
    comment = models.TextField(blank=True)
    date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'pay_payment_cluster_state_transitions'
        managed = False


class PaymentClusterQueue(models.Model):
    order_id = models.BigIntegerField(unique=True)
    modified = models.DateTimeField()
    id = models.IntegerField(primary_key=True)

    class Meta:
        db_table = u'pay_payment_cluster_queue'
        managed = False


class Capture(models.Model):
    id = models.IntegerField(primary_key=True)
    donation = models.ForeignKey('legacydonations.Donation', unique=True)
    capture_batch = models.ForeignKey('legacyconsolidations.CaptureBatch',
        null=True, blank=True
    )
    status = models.CharField(max_length=12)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    account_number = models.CharField(max_length=10)
    account_name = models.CharField(max_length=35)
    account_city = models.CharField(max_length=35)
    created = models.DateTimeField()

    class Meta:
        db_table = u'pay_captures'
        managed = False

    def donation(self):
        return self.donation_set.all()[0:1]
