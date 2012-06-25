from django.db import models


class Design(models.Model):
    """ Voucher Design. Designs for Voucher-pdfs """

    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    file = models.CharField(max_length=255)
    is_legacy = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = u'cou_designs'


class Batch(models.Model):
    """ Batches of Coupons (fka CouCouponsBatches) """

    id = models.IntegerField(primary_key=True)
    order = models.ForeignKey('payments.PaymentCluster',
        null=True, blank=True
    )
    member = models.ForeignKey('members.Member')
    coupon_amount = models.FloatField()
    total_amount = models.FloatField()
    currency = models.CharField(max_length=255)
    created = models.DateTimeField()
    status = models.CharField(max_length=255)

    class Meta:
        db_table = u'cou_coupons_batches'


class OrderLine(models.Model):
    """ Orderlines? """

    id = models.IntegerField(primary_key=True)
    member_id = models.IntegerField()
    design_id = models.IntegerField()
    coupontype = models.CharField(max_length=16, blank=True)
    from_field = models.CharField(
        max_length=255, db_column='from', blank=True
    ) # Field renamed because it was a Python reserved word.
    to = models.CharField(max_length=255)
    message = models.CharField(max_length=300)
    amount = models.DecimalField(
        null=True, max_digits=65535, decimal_places=65535, blank=True
    )
    receiver_email = models.CharField(max_length=255, blank=True)
    receiver_name = models.CharField(max_length=255, blank=True)
    receiver_address = models.CharField(max_length=255, blank=True)
    receiver_zipcode = models.CharField(max_length=255, blank=True)
    receiver_city = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'cou_order_lines'


class Voucher(models.Model):
    """ 1%VOUCHERS (fka CouCoupons) """

    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=255, unique=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=255)
    design = models.ForeignKey(Design)
    type = models.CharField(max_length=255)
    created = models.DateTimeField()
    receiver_name = models.CharField(max_length=255, blank=True)
    receiver_address = models.CharField(max_length=255, blank=True)
    receiver_zipcode = models.CharField(max_length=255, blank=True)
    receiver_city = models.CharField(max_length=255, blank=True)
    receiver_email = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    coupon_batch = models.ForeignKey(Batch)
    donation = models.ForeignKey('donations.Donation', null=True, blank=True)
    from_name = models.CharField(max_length=255, blank=True)
    to_name = models.CharField(max_length=255, blank=True)
    member = models.ForeignKey('members.Member')

    class Meta:
        db_table = u'cou_coupons'
