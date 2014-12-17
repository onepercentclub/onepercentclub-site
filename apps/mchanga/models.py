from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField


class MpesaPayment(models.Model):

    @classmethod
    def create_from_json(cls, pm):
        from bluebottle.projects.models import Project
        payment, created = cls.objects.get_or_create(mpesa_id=pm['mmp_trid'])
        if created:
            try:
                project = Project.objects.get(mchanga_account=pm['m-changa_acno'])
            except Project.DoesNotExist:
                project = None
            payment.mpesa_id = pm['mmp_trid']
            payment.project = project
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


class MpesaFundraiser(models.Model):

    @classmethod
    def create_from_json(cls, fr):
        account = fr['m-changa_acno']
        fundraiser, created = cls.objects.get_or_create(account=account)
        from bluebottle.projects.models import Project
        try:
            project = Project.objects.get(mchanga_account=account)
        except Project.DoesNotExist:
            project = None
        if created:
            fundraiser.account = account
            fundraiser.name = fr['fundraiser_name']
            fundraiser.status = fr['status']
            fundraiser.owner = fr['fundraiser_originator']
            fundraiser.link = fr['fundraiser_statement_link']
            fundraiser.project = project
        fundraiser.total_amount = fr['historical_amt']
        fundraiser.current_amount = fr['current_balance']
        fundraiser.payments_count = fr['payments_count']
        fundraiser.save()
        if project:
            project.update_amounts()

    project = models.ForeignKey('projects.Project', null=True)

    name =  models.CharField(max_length=100, blank=True)
    owner =  models.CharField(max_length=100, blank=True)
    link =  models.CharField(max_length=100, blank=True)
    account =  models.CharField(max_length=100, blank=True)

    total_amount = models.IntegerField(null=True)
    current_amount =  models.IntegerField(null=True)
    payment_count =   models.IntegerField(null=True)
    status =  models.CharField(max_length=10, blank=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

