class AbstractPaymentAdapter(object):
    """ 
    This is the base class that should be used by all Payment Adapters.
    """
    payment_info = None
    payment = None

    def get_payment(self):
        if not self.payment:
            raise Exception("Payment not set.")
        return self.payment

    def set_payment(self, payment):
        # TODO: Check if this is the right type
        self.payment = payment
        return payment

    def create_payment_info(self, *args, **kwargs):
        raise NotImplementedError

    def get_or_create_payment_info(self, *args, **kwargs):
        if not self.payment_info:
            self.payment_info = self.create_payment_info(*args, **kwargs)
        return self.payment_info

    def get_payment_info(self):
        if not self.payment_info:
            raise Exception("PaymentInfo not set. Create one with create_payment_info")
        return self.payment_info

    def get_url(self, **kwargs):
        # Returns the url the client should be redirected to to finish the payment.
        raise NotImplementedError

    def get_form(self, data):
        # Get the form for this payment
        raise NotImplementedError

