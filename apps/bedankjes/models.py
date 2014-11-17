from django.db import models
from django.db.models.signals import pre_save
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

        payload = {}
        payload['identifier'] = donation.user.username # A Friend of Mine has a list of predefined accounts
        payload['name'] = donation.user.get_full_name()
        payload['email'] = donation.user.email
        payload['project'] = donation.project.title
        payload['amount'] = donation.amount

        url = "http://31.3.103.106"
        
        print "Payload", json.dumps(payload)
        
        r = requests.post(url, data=json.dumps(payload))

        print "Status code", r.status_code
        print "Content-type", r.headers['content-type']
