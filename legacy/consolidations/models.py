from django.db import models


"""
Not sure. These tables have to do something with verfying payments.
Not only donation, but also payments to proj organization and fees
for PSP and 1%CLUB.

Mathijs: we'll do the actual PSP interaction with a certain level of
abstraction. Depends on results of PSP research.
"""


class Consolidation(models.Model):
    id = models.IntegerField(primary_key=True)
    created = models.DateTimeField()
    status = models.CharField(max_length=10)

    class Meta:
        db_table = u'con_consolidations'
        managed = False


class Settlement(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=12)
    consolidation = models.ForeignKey(Consolidation)
    project = models.ForeignKey('projects.Project', null=True, blank=True)
    status = models.CharField(max_length=10)
    num_donations = models.IntegerField()
    amount_registered = models.DecimalField(max_digits=14, decimal_places=4)
    amount_psp_fee = models.DecimalField(max_digits=14, decimal_places=4)
    amount_service_fee = models.DecimalField(max_digits=14, decimal_places=4)
    amount_organization_fee = models.DecimalField(
        max_digits=14, decimal_places=4
    )
    amount_bank_costs_direct = models.DecimalField(
        max_digits=14, decimal_places=4
    )
    amount_bank_costs_indirect = models.DecimalField(
        max_digits=14, decimal_places=4
    )
    amount_collected = models.DecimalField(max_digits=14, decimal_places=4)

    class Meta:
        db_table = u'con_settlements'
        managed = False

    def line(self):
        return self.project_settlement_set.all()


class SettlementLine(models.Model):
    id = models.IntegerField(primary_key=True)
    donation_line = models.ForeignKey('donations.DonationLine', unique=True)
    created = models.DateTimeField()
    amount_registered = models.DecimalField(max_digits=14, decimal_places=4)
    amount_psp_fee = models.DecimalField(max_digits=14, decimal_places=4)
    amount_service_fee = models.DecimalField(max_digits=14, decimal_places=4)
    amount_organization_fee = models.DecimalField(max_digits=14, decimal_places=4)
    amount_bank_costs_direct = models.DecimalField(max_digits=14, decimal_places=4)
    amount_bank_costs_indirect = models.DecimalField(max_digits=14, decimal_places=4)
    amount_collected = models.DecimalField(max_digits=14, decimal_places=4)
    settlement_id_project = models.ForeignKey(Settlement, null=True,
        db_column='settlement_id_project', blank=True,
        related_name='project_settlement'
    )
    settlement_id_organization = models.ForeignKey(Settlement, null=True,
        db_column='settlement_id_organization', blank=True,
        related_name='organization_settlement'
    )
    settlement_id_service = models.ForeignKey(Settlement, null=True,
        db_column='settlement_id_service', blank=True,
        related_name='service_settlement'
    )

    class Meta:
        db_table = u'con_settlement_lines'
        managed = False


class CaptureBatch(models.Model):
    id = models.IntegerField(primary_key=True)
    consolidation = models.ForeignKey(Consolidation, unique=True)
    status = models.CharField(max_length=10)

    class Meta:
        db_table = u'con_capture_batches'
        managed = False

    def captures(self):
        return self.capture_set.all()[0:5]


class RemittanceBatch(models.Model):
    id = models.IntegerField(primary_key=True)
    consolidation = models.ForeignKey(Consolidation, unique=True)
    status = models.CharField(max_length=10)

    class Meta:
        db_table = u'con_remittance_batches'
        managed = False


class Remittance(models.Model):
    id = models.IntegerField(primary_key=True)
    remittance_batch = models.ForeignKey(RemittanceBatch)
    type = models.CharField(max_length=12)
    settlement = models.ForeignKey(Settlement)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    account_number = models.CharField(max_length=10)
    account_name = models.CharField(max_length=35)
    account_city = models.CharField(max_length=35)
    description1 = models.CharField(max_length=32)
    description2 = models.CharField(max_length=32)
    description3 = models.CharField(max_length=32)

    class Meta:
        db_table = u'con_remittances'
        managed = False
