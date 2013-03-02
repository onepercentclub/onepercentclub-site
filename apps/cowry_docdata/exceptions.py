class DocDataException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return u'{0} {1}'.format(self.code, self.message)

    def __unicode__(self):
        return str(self)


class DocDataPaymentException(DocDataException):
    pass


class DocDataPaymentStatusException(DocDataException):
    pass
