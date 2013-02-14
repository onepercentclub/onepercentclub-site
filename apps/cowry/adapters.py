from django.utils.importlib import import_module


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

    def create_webmenu_payment(self, payment):
        raise NotImplementedError

    def update_payment_status(self, payment):
        raise NotImplementedError

    # TODO what to do about this method?
    def map_status(self, status):
        # return self.map_status(payment.payment_info.status)
        return status


