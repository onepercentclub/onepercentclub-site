from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.translation import ugettext as _
from celery import task

@task
def mail_new_voucher(voucher, *args, **kwargs):
    # TODO: Put this in config
    system_email = 'vouchers@1procentclub.nl'

    subject = _(u'You received a 1%VOUCHER')
    text_content = _(u'You received a 1%VOUCHER with this code: ') + voucher.code
    context = Context({'voucher': voucher})
    html_content = get_template('voucher_new.mail.html').render(context)
    msg = EmailMultiAlternatives(subject=subject, body=text_content, from_email=system_email,
                                 to=[voucher.receiver_email], cc=[voucher.sender_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@task
def mail_voucher_redeemed(voucher, *args, **kwargs):
    # TODO: Put this in config
    system_email = 'vouchers@1procentclub.nl'

    subject = voucher.receiver_name + ' ' + _(u'has redeemed a 1%VOUCHER you gave.')
    text_content = voucher.receiver_name + ' ' + _(u'has redeemed a 1%VOUCHER you gave.')
    context = Context({'voucher': voucher})
    html_content = get_template('voucher_redeemed.mail.html').render(context)
    msg = EmailMultiAlternatives(subject=subject, body=text_content, from_email=system_email,
                                 to=[voucher.receiver_email], cc=[voucher.sender_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


