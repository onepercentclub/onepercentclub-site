class PaymentException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return u'{0} {1}'.format(self.code, self.message)

    def __unicode__(self):
        return str(self)


class PaymentNotSet(PaymentException):
    pass


class PaymentMethodNotSet(PaymentException):
    pass


class PaymentAdapterNotSet(PaymentException):
    pass


class PaymentAdapterSettingsNotFound(PaymentException):
    pass


class PaymentMethodNotFound(PaymentException):
    pass
