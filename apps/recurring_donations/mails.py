from babel.dates import format_date
from babel.numbers import format_currency
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from celery import task


@task
def mail_monthly_donation_processed_notification(recurring_payment, recurring_order):
    site = 'https://' + Site.objects.get_current().domain
    receiver = recurring_payment.user

    # Compose the mail
    context = Context({'order': recurring_order,
                       'receiver_first_name': receiver.first_name.capitalize(),
                       'date': format_date(locale='nl_NL'),
                       'amount': format_currency(recurring_payment.amount / 100, 'EUR', locale='nl_NL'),
                       'site': site})
    subject = "Bedankt voor je maandelijkse support"
    text_content = get_template('monthly_donation.mail.txt').render(context)
    html_content = get_template('monthly_donation.mail.html').render(context)
    msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[receiver.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
