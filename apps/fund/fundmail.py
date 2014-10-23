from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver
from apps.fund.models import Donation, DonationStatuses
from apps.mail import send_mail
from django.utils.translation import ugettext as _


@receiver(pre_save, weak=False, sender=Donation)
def new_oneoff_donation(sender, instance, **kwargs):
    """
    Send project owner a mail if a new "one off" donation is done. We consider a donation done if the status is pending.
    """
    donation = instance

    # Only process the donation if it is of type "one off".
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

        name = _('Anonymous')

        if donation.user:
            if donation.user.first_name != '':
                name = donation.user.first_name

        if donation.fundraiser:
            send_mail(
                template_name='new_oneoff_donation_fundraiser.mail',
                subject=_('You received a new donation'),
                to=donation.fundraiser.owner,

                amount=(donation.amount / 100.0),
                donor_name=name,
                link='/go/fundraisers/{0}'.format(donation.fundraiser.id),
            )
        # Always email the project owner.
        send_mail(
            template_name='new_oneoff_donation.mail',
            subject=_('You received a new donation'),
            to=donation.project.owner,

            amount=(donation.amount / 100.0),
            donor_name=name,
            link='/go/projects/{0}'.format(donation.project.slug),
        )
