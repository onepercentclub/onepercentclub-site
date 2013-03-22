# coding=utf-8
import logging

from apps.cowry.adapters import AbstractPaymentAdapter
from django.conf import settings
from django.utils.http import urlencode
from django.utils import timezone
from suds.client import Client
from suds.plugin import MessagePlugin
from .exceptions import DocDataPaymentException
from .models import DocDataPaymentOrder, DocDataWebMenu, DocDataPayment

status_logger = logging.getLogger('cowry-docdata.status')
payment_logger = logging.getLogger('cowry-docdata.payment')


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
        'max_amount': 10000, # €100
        'restricted_countries': ('NL',),
        'supports_recurring': False,
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


class DocDataAPIVersionPlugin(MessagePlugin):
    """
    This adds the API version number to the body element. This is required for the DocData soap API.
    """
    def marshalled(self, context):
        body = context.envelope.getChild('Body')
        request = body[0]
        request.set('version', '1.0')


class DocdataPaymentAdapter(AbstractPaymentAdapter):
    # Mapping of DocData statuses to Cowry statuses.
    status_mapping = {
        'NEW': 'new',
        'STARTED': 'in_progress',
        'AUTHORIZED': 'in_progress',
        'PAID': 'in_progress',
        'CANCELLED': 'cancelled',
        'CHARGED-BACK': 'cancelled',
        'CONFIRMED_PAID': 'paid',
        'CONFIRMED_CHARGEDBACK': 'cancelled',
        'CLOSED_SUCCESS': 'paid',
        'CLOSED_CANCELLED': 'cancelled',
    }

    # TODO: Create defaults for this like the payment_methods
    id_to_model_mapping = {
        'dd-ideal': DocDataWebMenu,
        'dd-direct-debit': DocDataWebMenu,
        'dd-creditcard': DocDataWebMenu,
        'dd-webmenu': DocDataWebMenu,
    }

    def __init__(self):
        # TODO Make setting for this.
        self.test = True

        # Create the soap client.
        if self.test:
            # Test API URL.
            url = 'https://test.tripledeal.com/ps/services/paymentservice/1_0?wsdl'
        else:
            # Live API URL.
            url = 'https://tripledeal.com/ps/services/paymentservice/1_0?wsdl'
        self.client = Client(url, plugins=[DocDataAPIVersionPlugin()])

        # Setup the merchant soap object for use in all requests.
        self.merchant = self.client.factory.create('ns0:merchant')
        # TODO: Make this required if adapter is enabled (i.e. throw an error if not set instead of defaulting to dummy).
        self.merchant._name = getattr(settings, "COWRY_DOCDATA_MERCHANT_NAME", None)
        self.merchant._password = getattr(settings, "COWRY_DOCDATA_MERCHANT_PASSWORD", None)

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

    def create_payment_object(self, payment_method_id='', payment_submethod_id='', amount=0, currency=''):
        payment = DocDataPaymentOrder.objects.create(payment_method_id=payment_method_id,
                                                     payment_submethod_id=payment_submethod_id,
                                                     amount=amount, currency=currency)
        payment.save()
        return payment

    def create_remote_payment_order(self, payment):
        # Some preconditions.
        if payment.payment_order_key:
            raise DocDataPaymentException('ERROR', 'Cannot create two remote DocData Payment orders for same payment.')
        if not payment.payment_method_id:
            raise DocDataPaymentException('ERROR', 'payment_method_id is not set')

        # Preferences for the DocData system
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
        name.first = payment.first_name
        name.last = payment.last_name

        shopper = self.client.factory.create('ns0:shopper')
        shopper.gender = "U"  # Send unknown gender.
        shopper.language = language
        shopper.email = payment.email
        shopper._id = payment.customer_id
        shopper.name = name

        # Billing information.
        address = self.client.factory.create('ns0:address')
        address.street = payment.street
        address.houseNumber = 'N/A'
        # TODO No spaces allowed in postal code. Move to serializer?
        address.postalCode = payment.postal_code.replace(' ', '')
        address.city = payment.city

        country = self.client.factory.create('ns0:country')
        country._code = payment.country
        address.country = country

        billTo = self.client.factory.create('ns0:destination')
        billTo.address = address
        billTo.name = name

        if self.test:
            # TODO: Make a setting for the prefix. Note this is also used in status changed notification.
            # A unique code for testing.
            payment.merchant_order_reference = ('COWRY-' + str(timezone.now()))[:30]
        else:
            # TODO: Make a setting for the prefix. Note this is also used in status changed notification.
            payment.merchant_order_reference = 'COWRY-' + str(payment.id)

        # Save in case there's an error creating the payment order.
        payment.save()

        # Execute create payment order request.
        reply = self.client.service.create(self.merchant, payment.merchant_order_reference, paymentPreferences,
                                           menuPreferences, shopper, amount, billTo)
        if hasattr(reply, 'createSuccess'):
            payment.payment_order_key = reply['createSuccess']['key']
            payment.save()
        elif hasattr(reply, 'createError'):
            error = reply['createError']['error']
            raise DocDataPaymentException(error['_code'], error['value'])
        else:
            raise DocDataPaymentException('REPLY_ERROR',
                                          'Received unknown reply from DocData. Remote Payment not created.')
        payment.save()

    def get_payment_url(self, payment, return_url_base=None):
        """ Return the Payment URL """

        if not payment.payment_method_id or not self.id_to_model_mapping[payment.payment_method_id] == DocDataWebMenu:
            return None

        if not payment.payment_order_key:
            self.create_remote_payment_order(payment)

        # The basic parameters.
        params = {
            'payment_cluster_key': payment.payment_order_key,
            'merchant_name': self.merchant._name,
            'client_language': payment.language,
        }

        # Add a default payment method if the config has an id.
        payment_methods = self.get_payment_methods()
        if hasattr(payment_methods[payment.payment_method_id], 'id'):
            params['default_pm'] = payment_methods[payment.payment_method_id]['id'],

        # Add return urls.
        if return_url_base:
            params['return_url_success'] = return_url_base + '#/support/thanks'
            params['return_url_pending'] = return_url_base + '#/support/thanks'
            params['return_url_canceled'] = return_url_base + '#/support/thanks'
            params['return_url_error'] = return_url_base

        # Special parameters for iDeal.
        if payment.payment_method_id == 'dd-ideal' and payment.payment_submethod_id:
            params['ideal_issuer_id'] = payment.payment_submethod_id
            params['default_act'] = 'true'

        if self.test:
            payment_url_base = 'https://test.docdatapayments.com/ps/menu'
        else:
            payment_url_base = 'https://secure.docdatapayments.com/ps/menu'

        # Create a DocDataWebMenu when we need it.
        webmenu_payment = payment.latest_docdata_payment
        if not webmenu_payment or not isinstance(webmenu_payment, DocDataWebMenu):
            webmenu_payment = DocDataWebMenu()
            webmenu_payment.docdata_payment_order = payment

        webmenu_payment.payment_url = payment_url_base + '?' + urlencode(params)
        webmenu_payment.save()
        return webmenu_payment.payment_url

    def update_payment_status(self, payment, status_changed_notification=False):
        assert payment

        # Create the payment order if we need it.
        if not payment.payment_order_key:
            self.create_remote_payment_order(payment)

        # Execute status request.
        reply = self.client.service.status(self.merchant, payment.payment_order_key)
        if hasattr(reply, 'statusSuccess'):
            report = reply['statusSuccess']['report']
        elif hasattr(reply, 'statusError'):
            error = reply['statusError']['error']
            status_logger.error("{0} {1}".format(error['_code'], error['value']))
            return
        else:
            status_logger.error("Received unknown status reply from DocData.")
            return

        if not hasattr(report, 'payment'):
            if status_changed_notification:
                status_logger.warn(
                    "Status changed notification received for {0} but status report had no payment reports.".format(
                        payment.payment_order_key))
            return

        statusChanged = False
        for payment_report in report.payment:
            # Find or create the DocDataPayment for current report.
            ddpayment = DocDataPayment.objects.filter(payment_id=payment_report.id)
            if not ddpayment:
                status_logger.error("DocData status report has unknown payment: {0}".format(payment.payment_order_key))
                continue

            # Some additional checks.
            if not payment_report.paymentMethod == ddpayment.payment_methods['payment.payment_method_id'].id:
                status_logger.error(
                    "Payment methods do not match: {0} - {1}".format(payment.payment_order_key, ddpayment.payment_id))
                continue

            if not payment_report.authorization.status in DocDataPayment.statuses:
                # Note: We continue to process the payment status change on this error.
                status_logger.error(
                    "Received unknown status from DocData: {0}".format(payment_report.authorization.status))

            # Update the DocDataPayment status.
            if ddpayment.status != payment_report.authorization.status:
                status_logger.info("DocDataPayment status changed for payment id {0}: {1} -> {2}", payment_report.id,
                                   ddpayment.status, payment_report.authorization.status)
                ddpayment.status = payment_report.authorization.status
                ddpayment.save()
                statusChanged = True

        # Log a warning if we've received a status change notification and have no status changes.
        if status_changed_notification and not statusChanged:
            status_logger.warn(
                "Status changed notification received for {0} but no payment status change detected.".format(
                    payment.payment_order_key))

        # Use the latest DocDataPayment status to set the status on the Cowry Payment.
        ddpayment = payment.latest_docdata_payment
        lpr = report.payment[0]
        for payment_report in report.payment:
            if payment_report.id == ddpayment.payment_id:
                lpr = payment_report
                break

        new_status = self.map_status(ddpayment.status, report.approximateTotals, lpr.authorization)
        status_logger.info(
            "DocDataPaymentOrder status changed for payment order key {0}: {1} -> {1}".format(ddpayment.status,
                                                                                              new_status))
        payment.status = new_status
        payment.save()

    def map_status(self, status, totals=None, authorization=None):
        return super(DocdataPaymentAdapter, self).map_status(status)

        # TODO Use status change log to investigate if these overrides are needed.
        # Some status mapping overrides.

        # Integration Manual Order API 1.0 - Document version 1.0, 08-12-2012 - Page 33:
        # Safe route: The safest route to check whether all payments were made is for the merchants
        # to refer to the “Total captured” amount to see whether this equals the “Total registered
        # amount”. While this may be the safest indicator, the downside is that it can sometimes take a
        # long time for acquirers or shoppers to actually have the money transferred and it can be
        # captured.
        # if totals.totalRegistered == totals.totalCaptured:
        #     new_status = 'paid'

        # These overrides are really just guessing.
        # latest_capture = authorization.capture[-1]
        # if status == 'AUTHORIZED':
        #     if hasattr(authorization, 'refund') or hasattr(authorization, 'chargeback'):
        #         new_status = 'cancelled'
        #     if latest_capture.status == 'FAILED' or latest_capture == 'ERROR':
        #         new_status = 'failed'
        #     elif latest_capture.status == 'CANCELLED':
        #         new_status = 'cancelled'
