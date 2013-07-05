from .models import Payment
from .signals import payment_status_changed


class AbstractPaymentAdapter(object):
    """
    This is the abstract base class that should be used by all Payment Adapters.
    """
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
        payment.status = new_status
        payment.save()
        payment_status_changed.send(sender=Payment, instance=payment, old_status=old_status, new_status=new_status)
