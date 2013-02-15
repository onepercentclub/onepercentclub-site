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

    def get_payment_url(self, payment):
        raise NotImplementedError

    def update_payment_status(self, payment):
        raise NotImplementedError

    def map_status(self, status):
        if hasattr(self, 'status_mapping'):
            if status in self.status_mapping:
                return self.map_status(status)
        return status


