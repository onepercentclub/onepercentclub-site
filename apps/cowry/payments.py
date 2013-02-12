from .factory import _adapter_for_payment_method



def create_remote_payment_order(payment):
    adapter = _adapter_for_payment_method(payment.payment_method)
    adapter.create_remote_payment_order(payment)

def update_payment_status(payment):
    adapter = _adapter_for_payment_method(payment.payment_method)
    return adapter.update_payment_status()

def get_payment_url(payment):
    adapter = _adapter_for_payment_method(payment.payment_method)
    return adapter.get_payment_url(payment)

def cancel_payment(payment):
    raise NotImplementedError

def refund_payment(payment):
    raise NotImplementedError
