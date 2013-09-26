from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from .models import Payment, PaymentStatuses, PaymentLogLevels
from .signals import payment_status_changed


class AbstractPaymentAdapter(object):
    """
    This is the abstract base class that should be used by all Payment Adapters.
    """

    def __init__(self):
        self.test = not getattr(settings, "COWRY_LIVE_PAYMENTS", False)

    def get_payment_methods(self):
        raise NotImplementedError

    def create_payment_object(self, payment_method_id, payment_submethod_id, amount, currency):
        raise NotImplementedError

    def create_remote_payment_order(self, payment):
        raise NotImplementedError

    def get_payment_url(self, payment):
        raise NotImplementedError

    def update_payment_status(self, payment):
        raise NotImplementedError

    def cancel_payment(self, payment):
        raise NotImplementedError

    def update_payment_fee(self, payment, payment_method, payment_fees_setting, payment_logger):
        payment_fees = getattr(settings, payment_fees_setting, None)
        if payment_fees:
            if payment_method in payment_fees:
                payment_cost_setting = str(payment_fees[payment_method])
                if '%' in payment_cost_setting:
                    # Note: This assumes that the amount in the payment method will cover the full cost of the
                    # payment order. It seems that at least DocData allows multiple payments to make up the full
                    # order total. The method used here should be ok for 1%Club but it may not be suitable for others.
                    cost_percent = Decimal(payment_cost_setting.replace('%', '')) / 100
                    payment_cost = cost_percent * payment.amount
                else:
                    payment_cost = Decimal(payment_cost_setting) * 100

                # Set the base transaction fee.
                transaction_fee = Decimal(str(payment_fees['transaction_fee']))
                payment.fee = payment_cost.quantize(Decimal('1.'), rounding=ROUND_HALF_UP) + transaction_fee
                payment.save()

            else:
                payment_logger(payment, PaymentLogLevels.warn,
                               "Can't set payment fee for {0} because payment method is not in {1} config.".format(
                                   payment_method, payment_fees_setting))
        else:
            payment_logger(payment, PaymentLogLevels.warn,
                           "Can't set payment fee for {0} because {1} config is not in set.".format(
                               payment_method, payment_fees_setting))

    def _map_status(self, status):
        """
        Maps a PSP status to a Cowry Payment status using the status_mapping dict.
        Subclasses can safely use and/or override this method.
        """
        if hasattr(self, 'status_mapping'):
            if status in self.status_mapping:
                return self.status_mapping.get(status)
        return status

    def _change_status(self, payment, new_status):
        """
        Changes the Cowry Payment status to new_status and sends a single about the change.
        Subclasses must use this method to change statuses.
        """
        old_status = payment.status
        if old_status != new_status:
            if new_status not in PaymentStatuses.values:
                new_status = PaymentStatuses.unknown

            payment.status = new_status
            payment.save()

            payment_status_changed.send(sender=Payment, instance=payment, old_status=old_status, new_status=new_status)
