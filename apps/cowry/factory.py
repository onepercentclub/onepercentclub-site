from .models import Payment, PaymentMethod


class PaymentFactory(object):

    #adapter = DocdataPaymentAdapter()
    adapter = None
    payment = None
    payment_method = None

    def get_payment_methods(self):
        # TODO: Filter this based on country
        return PaymentMethod.objects.filter(active=True).all()

    def set_payment_method(self, id):
        payment_method = PaymentMethod.objects.get(pk=id)
        self.payment.payment_method = payment_method
        self.payment.save()

    def create_payment(self, *args, **kwargs):
        if not 'amount' in kwargs:
            Exception("Cannot create Payment. Amount not specified.")
        self.payment = Payment.objects.create(status=Payment.PaymentStatuses.started, amount=kwargs['amount'])
        self.payment.payment_method = PaymentMethod.objects.get(pk=1)
        self.payment.save()

        return self.payment

    def set_payment(self, payment):
        # TODO: Check if it's a Payment instance
        self.payment = payment
        return self.payment

    def get_payment(self):
        if not self.payment:
            raise Exception("No payment yet. Use create_payment to create one.")
        if not isinstance(self.payment, Payment):
            raise Exception("Set payment not of type Payment")
        return self.payment

    def create_payment_info(self, *args, **kwargs):
        adapter = self.get_adapter()
        payment = self.get_payment()
        adapter.set_payment(payment)
        payment.payment_info =  adapter.create_payment_info(*args, **kwargs)
        payment.save()
        return payment.payment_info

    def get_adapter(self):
        if not self.adapter:
            adapter = self.get_payment().payment_method.payment_adapter
            app_name = 'cowry_' + adapter.slug
            adapter_name = adapter.slug.title() + 'PaymentAdapter'
            mod = __import__('apps.' + app_name + '.adapter')
            app = getattr(mod, app_name)
            app_class = getattr(app, 'adapter')
            adapter_class = getattr(app_class, adapter_name)
            self.adapter = adapter_class()
            return self.adapter

    def check_payment(self):
        adapter = self.get_adapter()
        adapter.set_payment(self.get_payment())
        return adapter.check_payment_info()

