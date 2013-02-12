from django.utils.importlib import import_module


class AbstractPaymentAdapter(object):
    """
    This is the abstract base class that should be used by all Payment Adapters.
    """

    def get_payment_methods(self, amount, currency, country, recurring):
        raise NotImplementedError

    def get_payment_submethods(self, payment_method):
        raise NotImplementedError

    def create_payment_object(self, payment_method, payment_submethod, amount, currency):
        raise NotImplementedError

    def update_payment_status(self, payment, update):
        raise NotImplementedError

    # TODO what to do about this method?
    def map_status(self, status):
        # return self.map_status(payment.payment_info.status)
        return status


