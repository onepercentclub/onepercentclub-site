class PaymentException(Exception):
    """ Wrapper around Docdata error messages. """

    def __init__(self, message, error_list):
        self.message = message
        self.error_list = error_list

    def __str__(self):
        return '%s, messages: %s' % (self.message, ' '.join(self.error_list))

    def __unicode__(self):
        return str(self)


class PaymentStatusException(Exception):
    """ Thrown when unknown payment statuses are received. """

    def __init__(self, message, report_type, data=None):
        self.message = message
        self.report_type = report_type
        self.data = data

    def __str__(self):
        return '%s, report type %s, data %s' % (self.message, self.report_type, self.data)

    def __unicode__(self):
        return str(self)
    
    
class PaymentProcessNotSet(Exception):
    pass