from babel.dates import format_date
from babel.numbers import format_currency
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.translation import ugettext_lazy as _
from celery import task

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


def mail_new_oneoff_donation(donation):
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
    # alway email the project owner
    send_mail(
        template_name='new_oneoff_donation.mail',
        subject=_('You received a new donation'),
        to=donation.project.owner,

        amount=(donation.amount / 100.0),
        donor_name=name,
        link='/go/projects/{0}'.format(donation.project.slug),
    )
