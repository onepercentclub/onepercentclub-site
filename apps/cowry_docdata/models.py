from apps.cowry.models import PaymentInfo
from django.db import models

class DocdataPaymentInfo(PaymentInfo):

    transaction_id = models.CharField(max_length=100, blank=True)

    payment_cluster_key = models.CharField(max_length=255, blank=True)
    payment_cluster_id = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=255,default="", blank=True)

    client_id = models.CharField(max_length=255,default="", blank=True)
    client_email = models.CharField(max_length=255,default="")
    client_firstname = models.CharField(max_length=255,default="")
    client_lastname = models.CharField(max_length=255,default="")
    client_address = models.CharField(max_length=255,default="")
    client_zip = models.CharField(max_length=255,default="")
    client_city = models.CharField(max_length=255,default="")
    client_country = models.CharField(max_length=255,default="")

    class Meta:
        db_table = "payments_paymentinfo_docdata"

