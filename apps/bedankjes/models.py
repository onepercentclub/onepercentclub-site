from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings
from django.dispatch import receiver
from apps.fund.models import Donation, DonationStatuses # Old donation model
#from bluebottle.utils.model_dispatcher import get_donation_model
import requests
import json


# DONATION_MODEL = get_donation_model()

# @receiver(pre_save, sender=DONATION_MODEL)
# def post_to_friend_of_mine(sender, created, **kwargs):
#     if created:
#       print "New donation created!"


@receiver(pre_save, weak=False, sender=Donation)
def post_to_friend_of_mine(sender, instance, **kwargs):

    if not hasattr(settings, 'POST_A_FRIEND_OF_MINE'):
        return

    if not settings.POST_A_FRIEND_OF_MINE:
        return


    donation = instance

    # Only post to AFOM for one-off donations. 
    if donation.donation_type != Donation.DonationTypes.one_off:
        return

    # If the instance has no PK the previous status is unknown.
    if donation.pk:
        # NOTE: We cannot check the previous and future state of the ready attribute since it is set in the
        # Donation.save function.

        existing_donation = Donation.objects.get(pk=donation.pk)
        # If the existing donation is already pending, don't mail.
        if existing_donation.status in [DonationStatuses.pending, DonationStatuses.paid]:
            return

    # If the donation status will be pending, send a mail.
    if donation.status in [DonationStatuses.pending, DonationStatuses.paid]:

        if donation.fundraiser:
            user = donation.fundraiser.owner.username
        else:
            identifier = donation.project.owner.username

        payload = {}
        payload['identifier'] = identifier # A Friend of Mine has a list of predefined accounts
        payload['first_name'] = donation.user.first_name
        payload['last_name'] = donation.user.last_name
        payload['city'] = donation.user.location
        payload['email'] = donation.user.email
        payload['project'] = donation.project.title
        payload['amount'] = donation.amount

        url = "http://stage-onepercentclub.campaignapps.nl/api/donations/new"
                
        res = requests.post(url, data=json.dumps(payload))
