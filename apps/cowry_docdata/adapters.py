# coding=utf-8
import logging
import time
import unicodedata
from urllib2 import URLError
from apps.cowry.adapters import AbstractPaymentAdapter
from apps.cowry.models import PaymentStatuses, PaymentLogLevels
from django.conf import settings
from django.utils.http import urlencode
from suds.client import Client
from suds.plugin import MessagePlugin, DocumentPlugin
from .exceptions import DocDataPaymentException
from .models import DocDataPaymentOrder, DocDataPayment, DocDataWebDirectDirectDebit, DocDataPaymentLogEntry

logger = logging.getLogger(__name__)
cowry_docdata_logger = logging.getLogger('cowry.docdata')


# Workaround for SSL problem on Debian Wheezy connecting to DocData live payment address.
#
# if getattr(settings, "COWRY_LIVE_PAYMENTS", False):
#     import ssl
#     from ssl import SSLSocket
#
#     def wrap_socket(sock, keyfile=None, certfile=None,
#                     server_side=False, cert_reqs=ssl.CERT_NONE,
#                     ssl_version=ssl.PROTOCOL_SSLv3, ca_certs=None,
#                     do_handshake_on_connect=True,
#                     suppress_ragged_eofs=True, ciphers=None):
#
#         return SSLSocket(sock, keyfile=keyfile, certfile=certfile,
#                          server_side=server_side, cert_reqs=cert_reqs,
#                          ssl_version=ssl_version, ca_certs=ca_certs,
#                          do_handshake_on_connect=do_handshake_on_connect,
#                          suppress_ragged_eofs=suppress_ragged_eofs,
#                          ciphers=ciphers)
#
#     ssl.wrap_socket = wrap_socket


# These defaults can be overridden with the COWRY_PAYMENT_METHODS setting.
default_payment_methods = {
    'dd-ideal': {
        'id': 'IDEAL',
        'profile': 'ideal',
        'name': 'iDeal',
        'submethods': {
            '0081': 'Fortis',
            '0021': 'Rabobank',
            '0721': 'ING Bank',
            '0751': 'SNS Bank',
            '0031': 'ABN Amro Bank',
            '0761': 'ASN Bank',
            '0771': 'SNS Regio Bank',
            '0511': 'Triodos Bank',
            '0091': 'Friesland Bank',
            '0161': 'van Lanschot Bankiers'
        },
        'restricted_countries': ('NL',),
        'supports_recurring': False,
    },

    'dd-direct-debit': {
        'id': 'DIRECT_DEBIT',
        'profile': 'directdebit',
        'name': 'Direct Debit',
        'max_amount': 10000,  # €100
        'restricted_countries': ('NL',),
        'supports_recurring': True,
        'supports_single': False,
    },

    'dd-creditcard': {
        'profile': 'creditcard',
        'name': 'Credit Cards',
        'supports_recurring': False,
    },

    'dd-webmenu': {
        'profile': 'webmenu',
        'name': 'Web Menu',
        'supports_recurring': True,
    }
}


def docdata_payment_logger(payment, level, message):
    if level == PaymentLogLevels.error:
        cowry_docdata_logger.error("{0} - {1}".format(payment, message))
    log_entry = DocDataPaymentLogEntry(docdata_payment_order=payment, level=level, message=message)
    log_entry.save()


class DocDataAPIVersionPlugin(MessagePlugin):
    """
    This adds the API version number to the body element. This is required for the DocData soap API.
    """

    def marshalled(self, context):
        body = context.envelope.getChild('Body')
        request = body[0]
        request.set('version', '1.0')


class DocDataBrokenWSDLPlugin(DocumentPlugin):
    def parsed(self, context):
        """ Called after parsing a WSDL or XSD document. The context contains the url & document root. """
        # The WSDL for the live payments API incorrectly references the wrong location.
        if len(context.document.children) == 19 and len(context.document.children[18]) > 0:
            location_attribute = context.document.children[18].children[0].getChild('address').attributes[0]
            location_attribute.setValue('https://secure.docdatapayments.com:443/ps/services/paymentservice/1_0')


class DocDataPaymentAdapter(AbstractPaymentAdapter):
    # Mapping of DocData statuses to Cowry statuses. Statuses are from:
    #
    #   Integration Manual Order API 1.0 - Document version 1.0, 08-12-2012 - Page 35
    #
    # The documentation is incorrect for the following statuses:
    #
    #   Documented          Actual
    #   ==========          ======
    #
    #   CANCELLED           CANCELED
    #   CLOSED_CANCELED     CLOSED_CANCELED (guessed based on old api)
    #
    status_mapping = {
        'NEW': PaymentStatuses.new,
        'STARTED': PaymentStatuses.in_progress,
        'REDIRECTED_FOR_AUTHENTICATION': PaymentStatuses.in_progress,
        'AUTHORIZED': PaymentStatuses.pending,
        'AUTHORIZATION_REQUESTED': PaymentStatuses.pending,
        'PAID': PaymentStatuses.pending,
        'CANCELED': PaymentStatuses.cancelled,
        'CHARGED-BACK': PaymentStatuses.chargedback,
        'CONFIRMED_PAID': PaymentStatuses.paid,
        'CONFIRMED_CHARGEDBACK': PaymentStatuses.chargedback,
        'CLOSED_SUCCESS': PaymentStatuses.paid,
        'CLOSED_CANCELED': PaymentStatuses.cancelled,
    }

    id_to_model_mapping = {
        'dd-ideal': DocDataPayment,
        'dd-webdirect': DocDataWebDirectDirectDebit,
        'dd-webmenu': DocDataPayment,
    }

    def _init_docdata(self):
        """ Creates the DocData test or live Suds client. """
        error_message = 'Could not create Suds client to connect to DocData.'
        if self.test:
            # Test API.
            test_url = 'https://test.docdatapayments.com/ps/services/paymentservice/1_0?wsdl'
            logger.info('Using the test DocData API: {0}'.format(test_url))
            try:
                self.client = Client(test_url, plugins=[DocDataAPIVersionPlugin()])
            except URLError as e:
                self.client = None
                logger.error('{0} {1}'.format(error_message, str(e)))
            else:
                # Setup the merchant soap object with the test password for use in all requests.
                self.merchant = self.client.factory.create('ns0:merchant')
                self.merchant._name = getattr(settings, "COWRY_DOCDATA_MERCHANT_NAME", None)
                self.merchant._password = getattr(settings, "COWRY_DOCDATA_TEST_MERCHANT_PASSWORD", None)
        else:
            # Live API.
            live_url = 'https://secure.docdatapayments.com/ps/services/paymentservice/1_0?wsdl'
            logger.info('Using the live DocData API: {0}'.format(live_url))
            try:
                self.client = Client(live_url, plugins=[DocDataAPIVersionPlugin(), DocDataBrokenWSDLPlugin()])
            except URLError as e:
                self.client = None
                logger.error('{0} {1}'.format(error_message, str(e)))
            else:
                # Setup the merchant soap object for use in all requests.
                self.merchant = self.client.factory.create('ns0:merchant')
                self.merchant._name = getattr(settings, "COWRY_DOCDATA_MERCHANT_NAME", None)
                self.merchant._password = getattr(settings, "COWRY_DOCDATA_LIVE_MERCHANT_PASSWORD", None)

    def __init__(self):
        super(DocDataPaymentAdapter, self).__init__()
        self._init_docdata()

    def get_payment_methods(self):
        # Override the payment_methods if they're set. This isn't in __init__ because
        # we want to override the settings in the tests.
        if not hasattr(self, '_payment_methods'):
            settings_payment_methods = getattr(settings, 'COWRY_PAYMENT_METHODS', None)
            if settings_payment_methods:
                # Only override the parameters that are set.
                self._payment_methods = {}
                for pmi in settings_payment_methods:
                    settings_pm = settings_payment_methods[pmi]
                    if pmi in default_payment_methods:
                        default_pm = default_payment_methods[pmi]
                        for param in settings_pm:
                            default_pm[param] = settings_pm[param]
                        self._payment_methods[pmi] = default_pm
                    else:
                        self._payment_methods[pmi] = settings_pm
            else:
                self._payment_methods = default_payment_methods

        return self._payment_methods

    def create_payment_object(self, order, payment_method_id='', payment_submethod_id='', amount=0, currency=''):
        payment = DocDataPaymentOrder(payment_method_id=payment_method_id,
                                      payment_submethod_id=payment_submethod_id,
                                      amount=amount, currency=currency)
        payment.order = order
        payment.save()
        return payment

    def generate_merchant_order_reference(self, payment):
        other_payments = DocDataPaymentOrder.objects.filter(order=payment.order).exclude(id=payment.id).order_by('-merchant_order_reference')
        if not other_payments:
            return '{0}-0'.format(payment.order.order_number)
        else:
            latest_mor = other_payments[0].merchant_order_reference
            order_payment_nums = latest_mor.split('-')
            payment_num = int(order_payment_nums[1]) + 1
            return '{0}-{1}'.format(payment.order.order_number, payment_num)


    # TODO Find a way to use UTF-8 / unicode strings with Suds to make this truly international.
    def convert_to_ascii(self, value):
        """ Normalize / convert unicode characters to ascii equivalents. """
        if isinstance(value, unicode):
            return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        else:
            return value

    def create_remote_payment_order(self, payment):
        # Some preconditions.
        if payment.payment_order_id:
            raise DocDataPaymentException('ERROR', 'Cannot create two remote DocData Payment orders for same payment.')
        if not payment.payment_method_id:
            raise DocDataPaymentException('ERROR', 'payment_method_id is not set')

        # We can't do anything if DocData isn't available.
        if not self.client:
            self._init_docdata()
            if not self.client:
                logger.error("Suds client is not configured. Can't create a remote DocData payment order.")
                return

        # Preferences for the DocData system.
        paymentPreferences = self.client.factory.create('ns0:paymentPreferences')
        paymentPreferences.profile = self.get_payment_methods()[payment.payment_method_id]['profile'],
        paymentPreferences.numberOfDaysToPay = 5
        menuPreferences = self.client.factory.create('ns0:menuPreferences')

        # Order Amount.
        amount = self.client.factory.create('ns0:amount')
        amount.value = str(payment.amount)
        amount._currency = payment.currency

        # Customer information.
        language = self.client.factory.create('ns0:language')
        language._code = payment.language

        name = self.client.factory.create('ns0:name')
        name.first = self.convert_to_ascii(payment.first_name)
        name.last = self.convert_to_ascii(payment.last_name)

        shopper = self.client.factory.create('ns0:shopper')
        shopper.gender = "U"  # Send unknown gender.
        shopper.language = language
        shopper.email = payment.email
        shopper._id = payment.customer_id
        shopper.name = name

        # Billing information.
        address = self.client.factory.create('ns0:address')
        address.street = self.convert_to_ascii(payment.address)
        address.houseNumber = 'N/A'
        address.postalCode = payment.postal_code.replace(' ', '')  # Spaces aren't allowed in the DocData postal code.
        address.city = payment.city

        country = self.client.factory.create('ns0:country')
        country._code = payment.country
        address.country = country

        billTo = self.client.factory.create('ns0:destination')
        billTo.address = address
        billTo.name = name

        # Set the description if there's an order.
        description = payment.order.__unicode__()[:50]
        if not description:
            # TODO Add a setting for default description.
            description = "1%Club"

        payment.merchant_order_reference = self.generate_merchant_order_reference(payment)

        # Execute create payment order request.
        reply = self.client.service.create(self.merchant, payment.merchant_order_reference, paymentPreferences,
                                           menuPreferences, shopper, amount, billTo, description)


        if hasattr(reply, 'createSuccess'):
            payment.payment_order_id = str(reply['createSuccess']['key'])
            self._change_status(payment, PaymentStatuses.in_progress)  # Note: _change_status calls payment.save().
        elif hasattr(reply, 'createError'):
            payment.save()
            error = reply['createError']['error']
            error_message = "{0} {1}".format(error['_code'], error['value'])
            logger.error(error_message)
            # Log this error to db too.
            log_entry = DocDataPaymentLogEntry(docdata_payment_order=payment, level='warn', message=error_message)
            log_entry.save()

            raise DocDataPaymentException(error['_code'], error['value'])
        else:
            payment.save()
            error_message = 'Received unknown reply from DocData. Remote Payment not created.'
            logger.error(error_message)
            # Log this error to db too.
            log_entry = DocDataPaymentLogEntry(docdata_payment_order=payment, level='warn', message=error_message)
            log_entry.save()

            raise DocDataPaymentException('REPLY_ERROR', error_message)

    def cancel_payment(self, payment):
        # Some preconditions.
        if not self.client:
            logger.error("Suds client is not configured. Can't cancel a DocData payment order.")
            return

        if not payment.payment_order_id:
            logger.warn('Attempt to cancel payment on Order id {0} which has no payment_order_id.'.format(payment.payment_order_id))
            return

        # Execute create payment order request.
        reply = self.client.service.cancel(self.merchant, payment.payment_order_id)
        if hasattr(reply, 'cancelSuccess'):
            for docdata_payment in payment.docdata_payments.all():
                docdata_payment.status = 'CANCELLED'
                docdata_payment.save()
            self._change_status(payment, PaymentStatuses.cancelled)  # Note: change_status calls payment.save().
        elif hasattr(reply, 'cancelError'):
            error = reply['cancelError']['error']
            error_message = "{0} {1}".format(error['_code'], error['value'])
            logger.error(error_message)
            raise DocDataPaymentException(error['_code'], error['value'])
        else:
            error_message = 'Received unknown reply from DocData. Remote Payment not cancelled.'
            logger.error(error_message)
            raise DocDataPaymentException('REPLY_ERROR', error_message)

    def get_payment_url(self, payment, return_url_base=None):
        """ Return the Payment URL """

        if payment.amount <= 0 or not payment.payment_method_id or \
                not self.id_to_model_mapping[payment.payment_method_id] == DocDataPayment:
            return None

        if not payment.payment_order_id:
            self.create_remote_payment_order(payment)

        # The basic parameters.
        params = {
            'payment_cluster_key': payment.payment_order_id,
            'merchant_name': self.merchant._name,
            'client_language': payment.language,
        }

        # Add a default payment method if the config has an id.
        payment_methods = self.get_payment_methods()
        if hasattr(payment_methods[payment.payment_method_id], 'id'):
            params['default_pm'] = payment_methods[payment.payment_method_id]['id'],

        # Add return urls.
        if return_url_base:
            params['return_url_success'] = return_url_base + '/' + payment.language + '/#!/support/thanks/' + str(payment.order.id)
            params['return_url_pending'] = return_url_base + '/' + payment.language + '/#!/support/thanks/' + str(payment.order.id)
            # TODO This assumes that the order is always a donation order. These Urls will be used when buying vouchers
            # TODO too which is incorrect.
            params['return_url_canceled'] = return_url_base + '/' + payment.language + '/#!/support/donations'
            params['return_url_error'] = return_url_base + '/' + payment.language + '/#!/support/payment/error'

        # Special parameters for iDeal.
        if payment.payment_method_id == 'dd-ideal' and payment.payment_submethod_id:
            params['ideal_issuer_id'] = payment.payment_submethod_id
            params['default_act'] = 'true'

        if self.test:
            payment_url_base = 'https://test.docdatapayments.com/ps/menu'
        else:
            payment_url_base = 'https://secure.docdatapayments.com/ps/menu'

        # Create a DocDataPayment when we need it.
        docdata_payment = payment.latest_docdata_payment
        if not docdata_payment or not isinstance(docdata_payment, DocDataPayment):
            docdata_payment = DocDataPayment()
            docdata_payment.docdata_payment_order = payment
            docdata_payment.save()

        return payment_url_base + '?' + urlencode(params)

    def update_payment_status(self, payment, status_changed_notification=False):
        # Don't do anything if there's no payment or payment_order_id.
        if not payment or not payment.payment_order_id:
            return

        # Execute status request.
        reply = self.client.service.status(self.merchant, payment.payment_order_id)
        if hasattr(reply, 'statusSuccess'):
            report = reply['statusSuccess']['report']
        elif hasattr(reply, 'statusError'):
            error = reply['statusError']['error']
            error_message = "{0} {1}".format(error['_code'], error['value'])
            logger.error(error_message)
            docdata_payment_logger(payment, PaymentLogLevels.error, error_message)
            return
        else:
            error_message = "REPLY_ERROR Received unknown status reply from DocData."
            logger.error(error_message)
            docdata_payment_logger(payment, PaymentLogLevels.error, error_message)
            return

        if not hasattr(report, 'payment'):
            docdata_payment_logger(payment, PaymentLogLevels.info, "DocData status report has no payment reports.")
            return

        for payment_report in report.payment:
            # Find or create the correct payment object for current report.
            payment_class = self.id_to_model_mapping[payment.payment_method_id]
            try:
                ddpayment = payment_class.objects.get(payment_id=str(payment_report.id))
            except payment_class.DoesNotExist:
                ddpayment_list = payment.docdata_payments.filter(status='NEW')
                ddpayment_list_len = len(ddpayment_list)
                if ddpayment_list_len == 0:
                    ddpayment = payment_class()
                    ddpayment.docdata_payment_order = payment
                elif ddpayment_list_len == 1:
                    ddpayment = ddpayment_list[0]
                else:
                    docdata_payment_logger(payment, PaymentLogLevels.error,
                                           "Cannot determine where to save the payment report.")
                    continue

                # Save some information from the report.
                ddpayment.payment_id = str(payment_report.id)
                ddpayment.payment_method = str(payment_report.paymentMethod)
                ddpayment.save()

            # Some additional checks.
            if not payment_report.paymentMethod == ddpayment.payment_method:
                docdata_payment_logger(payment, PaymentLogLevels.warn,
                                       "Payment method from DocData doesn't match saved payment method. "
                                       "Storing the payment method received from DocData for payment id {0}: {1}".format(
                                           ddpayment.payment_id, payment_report.paymentMethod))
                ddpayment.payment_method = str(payment_report.paymentMethod)
                ddpayment.save()

            if not payment_report.authorization.status in self.status_mapping:
                # Note: We continue to process the payment status change on this error.
                docdata_payment_logger(payment, PaymentLogLevels.error,
                                       "Received unknown payment status from DocData: {0}".format(
                                           payment_report.authorization.status))

            # Update the DocDataPayment status.
            if ddpayment.status != payment_report.authorization.status:
                docdata_payment_logger(payment, PaymentLogLevels.info,
                                       "DocData payment status changed for payment id {0}: {1} -> {2}".format(
                                           payment_report.id, ddpayment.status, payment_report.authorization.status))
                ddpayment.status = str(payment_report.authorization.status)
                ddpayment.save()

        # Use the latest DocDataPayment status to set the status on the Cowry Payment.
        latest_ddpayment = payment.latest_docdata_payment
        latest_payment_report = None
        for payment_report in report.payment:
            if payment_report.id == latest_ddpayment.payment_id:
                latest_payment_report = payment_report
                break
        old_status = payment.status
        new_status = self._map_status(latest_ddpayment.status, payment, report.approximateTotals,
                                      latest_payment_report.authorization)

        # Detect a nasty error condition that needs to be manually fixed.
        total_registered = report.approximateTotals.totalRegistered
        if new_status != PaymentStatuses.cancelled and total_registered != payment.order.total:
            docdata_payment_logger(payment, PaymentLogLevels.error,
                                   "Order total: {0} does not equal Total Registered: {1}.".format(payment.order.total,
                                                                                                   total_registered))

        # TODO: Move this logging to AbstractPaymentAdapter when PaymentLogEntry is not abstract.
        if old_status != new_status:
            if new_status not in PaymentStatuses.values:
                docdata_payment_logger(payment, PaymentLogLevels.error,
                                       "Payment status changed {0} -> {1}".format(old_status, PaymentStatuses.unknown))
            else:
                docdata_payment_logger(payment, PaymentLogLevels.info,
                                       "Payment status changed {0} -> {1}".format(old_status, new_status))

        self._change_status(payment, new_status)  # Note: change_status calls payment.save().

        # Set the payment fee when Payment status is pending or paid.
        if payment.status == PaymentStatuses.pending or payment.status == PaymentStatuses.paid:
            self.update_payment_fee(payment, payment.latest_docdata_payment.payment_method, 'COWRY_DOCDATA_FEES',
                                    docdata_payment_logger)

    def _map_status(self, status, payment=None, totals=None, authorization=None):
        new_status = super(DocDataPaymentAdapter, self)._map_status(status)

        # Some status mapping overrides.
        #
        # Integration Manual Order API 1.0 - Document version 1.0, 08-12-2012 - Page 33:
        #
        # Safe route: The safest route to check whether all payments were made is for the merchants
        # to refer to the “Total captured” amount to see whether this equals the “Total registered
        # amount”. While this may be the safest indicator, the downside is that it can sometimes take a
        # long time for acquirers or shoppers to actually have the money transferred and it can be
        # captured.
        #
        if status == 'AUTHORIZED':
            registered_captured_logged = False

            if totals.totalRegistered == totals.totalCaptured:

                payment_sum = totals.totalCaptured - totals.totalChargedback - totals.totalRefunded

                if payment_sum > 0:
                    new_status = PaymentStatuses.paid

                elif payment_sum == 0:
                    docdata_payment_logger(payment, PaymentLogLevels.info,
                                           "Total Registered: {0} Total Captured: {1} Total Chargedback: {2} Total Refunded: {3}".format(
                                               totals.totalRegistered, totals.totalCaptured, totals.totalChargedback, totals.totalRefunded))
                    registered_captured_logged = True

                    # FIXME: Add chargeback fee somehow (currently €0.50).
                    # Chargeback.
                    if totals.totalCaptured == totals.totalChargedback:
                        if hasattr(authorization, 'chargeback') and len(authorization['chargeback']) > 0:
                            if hasattr(authorization['chargeback'][0], 'reason'):
                                docdata_payment_logger(payment, PaymentLogLevels.info,
                                                       "Payment chargedback: {0}".format(authorization['chargeback'][0]['reason']))
                        else:
                            docdata_payment_logger(payment, PaymentLogLevels.info, "Payment chargedback.")
                        new_status = PaymentStatuses.chargedback

                    # Refund.
                    # TODO: Log more info from refund when we have an example.
                    if totals.totalCaptured == totals.totalRefunded:
                        docdata_payment_logger(payment, PaymentLogLevels.info, "Payment refunded.")
                        new_status = PaymentStatuses.refunded

                    payment.amount = 0
                    payment.save()

                else:
                    docdata_payment_logger(payment, PaymentLogLevels.error,
                                           "Total Registered: {0} Total Captured: {1} Total Chargedback: {2} Total Refunded: {3}".format(
                                               totals.totalRegistered, totals.totalCaptured, totals.totalChargedback, totals.totalRefunded))
                    registered_captured_logged = True
                    docdata_payment_logger(payment, PaymentLogLevels.error,
                                           "Captured, chargeback and refunded sum is negative. Please investigate.")
                    new_status = PaymentStatuses.unknown

            if not registered_captured_logged:
                docdata_payment_logger(payment, PaymentLogLevels.info,
                                       "Total Registered: {0} Total Captured: {1}".format(totals.totalRegistered,
                                                                                          totals.totalCaptured))

        return new_status

        # TODO Use status change log to investigate if these overrides are needed.
        # # These overrides are really just guessing.
        # latest_capture = authorization.capture[-1]
        # if status == 'AUTHORIZED':
        #     if hasattr(authorization, 'refund') or hasattr(authorization, 'chargeback'):
        #         new_status = 'cancelled'
        #     if latest_capture.status == 'FAILED' or latest_capture == 'ERROR':
        #         new_status = 'failed'
        #     elif latest_capture.status == 'CANCELLED':
        #         new_status = 'cancelled'


class WebDirectDocDataDirectDebitPaymentAdapter(DocDataPaymentAdapter):
    def get_payment_url(self, payment, return_url_base=None):
        raise NotImplementedError

    def generate_merchant_order_reference(self, payment):
        if self.test:
            # For testing we need unique merchant order references that are not based on the order number.
            return str(time.time()).replace('.', '-')
        else:
            return super(WebDirectDocDataDirectDebitPaymentAdapter, self).generate_merchant_order_reference(payment)

    def start_payment(self, payment, recurring_payment):
        # Some preconditions.
        if not self.client:
            raise DocDataPaymentException('ERROR',
                                          "Suds client is not configured. Can't start a DocData WebDirect payment.")
        if not payment.payment_order_id:
            raise DocDataPaymentException('ERROR',
                                          "Attempt to start WebDirect payment on Order id {0} which has no payment_order_id.".format(
                                              payment.payment_order_id))

        paymentRequestInput = self.client.factory.create('ns0:paymentRequestInput')

        # We only need to set amount because of bug in suds library. Otherwise it defaults to order amount.
        amount = self.client.factory.create('ns0:amount')
        amount.value = str(payment.amount)
        amount._currency = payment.currency
        paymentRequestInput.paymentAmount = amount

        paymentRequestInput.paymentMethod = 'DIRECT_DEBIT'

        directDebitPaymentInput = self.client.factory.create('ddp:directDebitPaymentInput')
        directDebitPaymentInput.iban = recurring_payment.iban
        directDebitPaymentInput.bic = recurring_payment.bic
        directDebitPaymentInput.holderCity = self.convert_to_ascii(recurring_payment.city)
        directDebitPaymentInput.holderName = self.convert_to_ascii(recurring_payment.name)

        country = self.client.factory.create('ns0:country')
        country._code = payment.country
        directDebitPaymentInput.holderCountry = country

        paymentRequestInput.directDebitPaymentInput = directDebitPaymentInput

        # Execute start payment request.
        reply = self.client.service.start(self.merchant, payment.payment_order_id, paymentRequestInput)
        if hasattr(reply, 'startSuccess'):

            self._change_status(payment, PaymentStatuses.in_progress)  # Note: _change_status calls payment.save().

            update_docdata_webdirect_direct_debit_payment(payment, str(reply['startSuccess']['paymentId']),
                                                          recurring_payment)

        elif hasattr(reply, 'startError'):
            error = reply['startError']['error']
            error_message = "{0} {1}".format(error['_code'], error['value'])
            logger.error(error_message)
            raise DocDataPaymentException(error['_code'], error['value'])

        else:
            error_message = 'Received unknown reply from DocData. WebDirect payment not created.'
            logger.error(error_message)
            raise DocDataPaymentException('REPLY_ERROR', error_message)


# TODO This method (and delay) should be processed asynchronously by celery.
def update_docdata_webdirect_direct_debit_payment(payment, payment_id, recurring_payment):
    # The delay is here to give DocData some time to call our status changed API which creates the
    # DocDataWebDirectDirectDebit object.
    time.sleep(6)
    try:
        ddpayment = DocDataWebDirectDirectDebit.objects.get(payment_id=payment_id)
    except DocDataWebDirectDirectDebit.DoesNotExist:
        # Create the DocDataPayment object to save the info and statuses for the WebDirect payment.
        ddpayment = DocDataWebDirectDirectDebit()
        ddpayment.docdata_payment_order = payment
        ddpayment.payment_method = 'DIRECT_DEBIT'
        ddpayment.payment_id = payment_id

    ddpayment.account_city = recurring_payment.city
    ddpayment.account_name = recurring_payment.name
    ddpayment.iban = recurring_payment.iban
    ddpayment.bic = recurring_payment.bic
    ddpayment.save()
