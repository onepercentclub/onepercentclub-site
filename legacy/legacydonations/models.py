'''
Created on May 24, 2012

@author: gannetson
'''
from django.db import models


class Donation(models.Model):
    """ Donations."""

    id = models.IntegerField(primary_key=True)
    member = models.ForeignKey('legacymembers.Member')
    type = models.CharField(max_length=10)
    status = models.CharField(max_length=12)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    meta_considered_safe = models.SmallIntegerField()
    created = models.DateTimeField()
    changed_to_safe = models.DateTimeField(null=True, blank=True)
    payment_cluster = models.ForeignKey('legacypayments.PaymentCluster',
        null=True, blank=True, db_column='order_id'
    )
    automatic_donation = models.SmallIntegerField()
    projects = models.ManyToManyField('legacyprojects.Project',
        through='DonationLine', related_name='projectdonations'
    )

    class Meta:
        db_table = u'don_donations'
        managed = False

    def lines(self):
        return DonationLine.objects.filter(donation=self)

    def __unicode__(self):
        return u'%f on %s from %s' % (
            self.amount, self.created, self.member
        )


class DonationLine(models.Model):
    """ Links a project to a donation """

    id = models.IntegerField(primary_key=True)
    donation = models.ForeignKey('legacydonations.Donation')
    project = models.ForeignKey('legacyprojects.Project')
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = u'don_donation_lines'
        managed = False

    def status(self):
        return self.donation.status

    def __unicode__(self):
        return u'%f from donation %s to %s' % (
            self.amount, self.donation, self.project
        )


class Thanks(models.Model):
    """"
    Video message as thank-you to a donation made during Toeter-campagne
    """

    id = models.IntegerField(primary_key=True)
    donation = models.ForeignKey(Donation)
    twitter = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    create_date = models.DateTimeField()
    video_date = models.DateTimeField(null=True, blank=True)
    video_link = models.CharField(max_length=255, blank=True)
    anonymous = models.NullBooleanField(null=True, blank=True)
    active = models.NullBooleanField(null=True, blank=True)
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'don_donation_thanks'
        managed = False

    def image(self):
        return 'http://i1.ytimg.com/vi/%s/1.jpg' % self.video_link

    def link(self):
        return 'http://www.youtube.com/embed/%s?wmode=transparent' \
            % self.video_link

    def getName(self):
        if self.anonymous:
            return 'I'
        return self.firstname.upper()

    def amount(self):
        return self.donation.amount

    def __unicode__(self):
        return u'For donation %s' % self.donation


class PortfolioLine(models.Model):
    """ Projects specifically selected for monthly payments by members """

    id = models.IntegerField(primary_key=True)
    member = models.ForeignKey('legacymembers.Member')
    project = models.ForeignKey('legacyprojects.Project')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created = models.DateTimeField()

    class Meta:
        db_table = u'don_portfolio_lines'
        managed = False

    def __unicode__(self):
        return u'%f on %s from %s to %s' % (
            self.amount, self.created, self.member, self.project
        )


class External(models.Model):
    """ External Donation. Currently used for the Mpesa pilot """

    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=255, blank=True)
    params = models.TextField(blank=True)
    status = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(
        null=True, max_digits=12, decimal_places=3, blank=True
    )
    currency = models.CharField(max_length=3, blank=True)
    donation = models.ForeignKey(Donation)
    order_id = models.CharField(max_length=255, blank=True)
    date_created = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'don_donation_external'
        managed = False

    def __unicode__(self):
        return u'%f for %s' % (
            self.amount, self.donation
        )
