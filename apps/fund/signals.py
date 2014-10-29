import logging
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver
from apps.cowry.models import Payment, PaymentStatuses
from apps.cowry.signals import payment_status_changed
from apps.fund.models import DonationStatuses, OrderStatuses, Donation

USER_MODEL = get_user_model()

logger = logging.getLogger(__name__)

@receiver(payment_status_changed, sender=Payment)
def process_payment_status_changed(sender, instance, old_status, new_status, **kwargs):
    # Payment statuses: new
    #                   in_progress
    #                   pending
    #                   paid
    #                   failed
    #                   cancelled
    #                   chargedback
    #                   refunded
    #                   unknown

    order = instance.order

    #
    # Payment: new -> in_progress
    #
    if old_status == PaymentStatuses.new and new_status == PaymentStatuses.in_progress:
        # Donations.
        for donation in order.donations.all():
            donation.status = DonationStatuses.in_progress
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.
        #for voucher in order.vouchers.all():
        #    process_voucher_order_in_progress(voucher)

    #
    # Payment: -> cancelled; Order is 'current'
    #
    if new_status == PaymentStatuses.cancelled and order.status == OrderStatuses.current:

        # Donations.
        for donation in order.donations.all():
            donation.status = DonationStatuses.new
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> cancelled; Order is 'closed'
    #
    elif new_status == PaymentStatuses.cancelled and order.status == OrderStatuses.closed:
        if order.status != OrderStatuses.closed:
            order.status = OrderStatuses.closed
            order.save()

        # Donations.
        for donation in order.donations.all():
            donation.status = DonationStatuses.failed
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> cancelled; Order is not 'closed' or 'current'
    #
    elif new_status == PaymentStatuses.cancelled:
        logger.error("PaymentStatuses.cancelled when Order {0} has status {1}.".format(order.id, order.status))

    #
    # Payment: -> pending
    #
    if new_status == PaymentStatuses.pending:
        if order.status != OrderStatuses.closed:
            order.status = OrderStatuses.closed
            order.save()

        # Donations.
        for donation in order.donations.all():
            donation.status = DonationStatuses.pending
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> paid
    #
    if new_status == PaymentStatuses.paid:
        if order.status != OrderStatuses.closed:
            order.status = OrderStatuses.closed
            order.save()

        # Donations.
        for donation in order.donations.all():
            donation.status = DonationStatuses.paid
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> failed, refunded or chargedback
    #
    if new_status in [PaymentStatuses.failed, PaymentStatuses.refunded, PaymentStatuses.chargedback]:
        if order.status != OrderStatuses.closed:
            order.status = OrderStatuses.closed
            order.save()

        # Donations.
        for donation in order.donations.all():
            donation.status = DonationStatuses.failed
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.
        #for voucher in order.vouchers.all():
        #    voucher.status = VoucherStatuses.cancelled
        #    voucher.save()


#Change project phase according to donated amount
@receiver(post_save, weak=False, sender=Donation)
def update_project_after_donation(sender, instance, created, **kwargs):
    # Skip all post save logic during fixture loading.
    if kwargs.get('raw', False):
        return

    project = instance.project

    # Don't look at donations that are just created.
    if instance.status not in [DonationStatuses.in_progress, DonationStatuses.new]:
        project.update_money_donated()
        project.update_popularity()
        project.update_status_after_donation()


@receiver(post_save, weak=False, sender=USER_MODEL)
def cancel_recurring_payment_user_soft_delete(sender, instance, created, **kwargs):
    if created:
        return

    if hasattr(instance, 'recurringdirectdebitpayment') and instance.deleted:
        recurring_payment = instance.recurringdirectdebitpayment
        recurring_payment.active = False
        recurring_payment.save()


@receiver(post_delete, weak=False, sender=USER_MODEL)
def cancel_recurring_payment_user_delete(sender, instance, **kwargs):

    if hasattr(instance, 'recurringdirectdebitpayment'):
        recurring_payment = instance.recurringdirectdebitpayment
        recurring_payment.delete()

