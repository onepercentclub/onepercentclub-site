from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField


class MpesaPayment(models.Model):

    @classmethod
    def create_from_json(cls, pm):
        payment, created = cls.objects.get_or_create(mpesa_id=pm['m-pesa_tr_id'])
        if created:
            payment.mpesa_id = pm['m-pesa_tr_id']
            payment.amount = pm['amount']
            payment.mchanga_account = pm['m-changa_acno']
            payment.mpesa_phone = pm['contributor_mobno']
            payment.mpesa_name = pm['contributor_name']
            payment.date = pm['payment_date']
            payment.fundraiser_name = pm['fundraiser_name']
            payment.save()

    project = models.ForeignKey('projects.Project', null=True)
    amount = models.IntegerField(null=True)
    currency = models.CharField(max_length=10, blank=True)
    fundraiser_name = models.CharField(max_length=100, blank=True)
    mchanga_account = models.CharField(max_length=100, blank=True)
    mpesa_id = models.CharField(max_length=100, blank=True)
    mpesa_name = models.CharField(max_length=100, blank=True)
    mpesa_phone = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(null=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))



"""
Example data:

"fundraiser_name": "Arts For Life",
"m-changa_acno": "1489",
"m-pesa_tr_id": "FQ10AI934",
"amount": "10",
"contributor_mobno": "254720978838",
"contributor_name": "JEFKINE KAFUNAH",
"payment_date": "2014-09-09 00:46:18"
"""