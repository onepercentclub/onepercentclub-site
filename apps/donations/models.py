from django.dispatch import receiver
from django.db.models.signals import pre_save
from apps.fund.models import Order, OrderStatuses, Donation, DonationStatuses, RecurringDirectDebitPayment
from apps.projects.models import Project
from apps.projects.signals import project_funded

from .mails import mail_project_funded_monthly_donor_notification, mail_new_oneoff_donation


# The monthly donor email will be sent under these conditions:
#
# 1) A user has manually selected a project for a monthly donation.
# 2) The monthly donation is active.
#
# The email is sent regardless of how the project became full. For instance, the email will be sent if the project
# becomes full during the month by a single donation and if it becomes full during the monthly donation batch job.
#
# The email will only be sent the first time that the project becomes full. If a donation fails and the project moves
# back to the campaign phase and then subsequently becomes full again, the email will not be sent a second time.
#
@receiver(project_funded, weak=False, sender=Project, dispatch_uid="email-monthly-donor-project-funded")
def email_monthly_donor_project_funded(sender, instance, first_time_funded, **kwargs):
    """
    Sends an email to users that have the funded project in their monthly shopping cart and have their monthly
    donation turned on.
    """
    # A project can become funded multiple times if pending donations fail. Only send this email the first time that
    # the project becomes funded.
    if first_time_funded:
        for order in Order.objects.filter(status=OrderStatuses.recurring):
            for donation in order.donations.all():
                if donation.project == instance:
                    # Only send the email if the monthly payment is turned on.
                    try:
                        recurring_payment = RecurringDirectDebitPayment.objects.get(user=order.user)
                    except RecurringDirectDebitPayment.DoesNotExist:
                        pass
                    else:
                        if recurring_payment.active:
                            mail_project_funded_monthly_donor_notification(donation.user, instance)


@receiver(pre_save, sender=Donation, dispatch_uid="new_oneoff_donation")
def new_oneoff_donation(sender, instance, **kwargs):
    """
    Send project owner a mail if a new "one off" donation is done. We consider a donation done if the status is pending.
    """
    # Only process the donation if it is of type "one off".
    if instance.donation_type != Donation.DonationTypes.one_off:
        return

    # If the instance has no PK the previous status is unknown.
    if instance.pk:
        # NOTE: We cannot check the previous and future state of the ready attribute since it is set in the
        # Donation.save function.

        existing_donation = Donation.objects.get(pk=instance.pk)
        # If the existing donation is already pending, don't mail.
        if existing_donation.status == DonationStatuses.pending:
            return

    # If the donation status will be pending, send a mail.
    if instance.status == DonationStatuses.pending:
        mail_new_oneoff_donation(instance)
