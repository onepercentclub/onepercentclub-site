from django.dispatch import receiver
from apps.fund.models import Order, OrderStatuses, RecurringDirectDebitPayment
from apps.projects.models import Project
from apps.projects.signals import project_funded

from .mails import *


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


