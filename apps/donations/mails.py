from apps.fund.models import DonationStatuses, Donation
from babel.dates import format_date
from babel.numbers import format_currency
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver
from django.template.loader import get_template
from django.template import Context
from django.utils.translation import ugettext_lazy as _
from celery import task

import time

from apps.mail import send_mail


@task
def mail_monthly_donation_processed_notification(recurring_payment, recurring_order):
    # TODO: Use English base and the regular translation mechanism.
    receiver = recurring_payment.user

    context = Context({'order': recurring_order,
                       'receiver_first_name': receiver.first_name.capitalize(),
                       'date': format_date(locale='nl_NL'),
                       'amount': format_currency(recurring_payment.amount / 100, 'EUR', locale='nl_NL'),
                       'site': 'https://' + Site.objects.get_current().domain})

    subject = "Bedankt voor je maandelijkse support"
    text_content = get_template('monthly_donation.nl.mail.txt').render(context)
    html_content = get_template('monthly_donation.nl.mail.html').render(context)
    msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[receiver.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@task
def mail_project_funded_monthly_donor_notification(receiver, project):
    # TODO: Use English base and the regular translation mechanism.
    context = Context({'receiver_first_name': receiver.first_name.capitalize(),
                       'project': project,
                       'link': '/go/projects/{0}'.format(project.slug),
                       'site': 'https://' + Site.objects.get_current().domain})

    subject = "Gefeliciteerd: project afgerond!"
    text_content = get_template('project_full_monthly_donor.nl.mail.txt').render(context)
    html_content = get_template('project_full_monthly_donor.nl.mail.html').render(context)
    msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[receiver.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@task
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

        if donation.user:
            name = donation.user.first_name
        else:
            name = _('Anonymous')

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
