from django.dispatch import receiver
from apps.fund.models import Order, OrderStatuses
from apps.projects.models import Project
from apps.projects.signals import project_funded
from .mails import mail_project_funded_monthly_donor_notification


@receiver(project_funded, weak=False, sender=Project, dispatch_uid="email-monthly-donor-project-funded")
def email_monthly_donor_project_funded(sender, instance, first_time_funded, **kwargs):
    # A project can become funded multiple times if pending donations fail. Only send this email the first time that
    # the project becomes funded.
    if first_time_funded:
        # Send an email to any user that has this project in their monthly shopping cart.
        for order in Order.objects.filter(status=OrderStatuses.recurring):
            for donation in order.donations.all():
                if donation.project == instance:
                    mail_project_funded_monthly_donor_notification(donation.user, instance)
