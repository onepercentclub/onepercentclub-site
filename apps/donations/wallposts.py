from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from apps.fund.models import Donation, DonationStatuses
from bluebottle.wallposts.models import SystemWallpost


@receiver(post_save, weak=False, sender=Donation)
def create_donation_post(sender, instance, **kwargs):

    donation = instance
    if donation.status in [DonationStatuses.paid, DonationStatuses.pending]:
        donation_type = ContentType.objects.get_for_model(donation)
        post = SystemWallpost.objects.filter(related_id=donation.id).filter(related_type=donation_type).all()
        if len(post) < 1:
            if donation.donation_type in [Donation.DonationTypes.one_off, Donation.DonationTypes.voucher]:

                if donation.voucher:
                    post = SystemWallpost()
                    post.content_object = donation.project
                    post.related_object = donation.voucher
                    post.author = donation.user
                    post.ip = '127.0.0.1'
                    post.save()

                elif donation.fundraiser:
                    # Post on Project Wall.
                    post = SystemWallpost()
                    post.content_object = donation.project
                    post.related_object = donation
                    post.author = donation.user
                    post.ip = '127.0.0.1'
                    post.save()

                    # Post on FundRaiser Wall.
                    post = SystemWallpost()
                    post.content_object = donation.fundraiser
                    post.related_object = donation
                    post.author = donation.user
                    post.ip = '127.0.0.1'
                    post.save()

                else:
                    post = SystemWallpost()
                    post.content_object = donation.project
                    post.related_object = donation
                    post.author = donation.user
                    post.ip = '127.0.0.1'
                    post.save()
