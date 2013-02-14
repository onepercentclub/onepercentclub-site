# coding=utf-8
from apps.cowry.adapters import AbstractPaymentAdapter
from apps.cowry_docdata.models import DocDataPaymentOrder, DocDataWebMenu
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.http import urlencode
from django.utils import timezone
from suds.client import Client
from suds.plugin import MessagePlugin
from .exceptions import DocDataPaymentException


class DocDataAPIVersionPlugin(MessagePlugin):
    """ This adds the API version number to the body element. This is required for the DocData soap API."""

    def marshalled(self, context):
        body = context.envelope.getChild('Body')
        request = body[0]
        request.set('version', '1.0')
        print body


class DocdataPaymentAdapter(AbstractPaymentAdapter):
    """
        Docdata payments
    """

    live_api_url = 'https://tripledeal.com/ps/services/paymentservice/1_0?wsdl'
    test_api_url = 'https://test.tripledeal.com/ps/services/paymentservice/1_0?wsdl'

    id_to_model_mapping = {
        'dd-ideal': DocDataWebMenu,
        'dd-mastercard': DocDataWebMenu,
        'dd-visa': DocDataWebMenu,
        'dd-direct-debit': DocDataWebMenu,
    }

    payment_methods = {
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

        'dd-mastercard': {
            'id': 'MASTERCARD',
            'profile': 'mastercard',
            'name': 'Mastercard',
            'supports_recurring': False,
        },

        'dd-visa': {
            'id': 'VISA',
            'profile': 'visa',
            'name': 'Visa',
            'supports_recurring': False,
        },

        'dd-direct-debit': {
            'id': 'DIRECT_DEBIT',
            'profile': 'directdebit',
            'name': 'Direct Debit',
            'max_amount': 10000, # €100
            'supports_recurring': False,
        },
    }

    def __init__(self):

        # TODO Make setting for this.
        self.test = True

        # Create the soap client.
        if self.test:
            url = self.test_api_url
        else:
            url = self.live_api_url
        self.client = Client(url, plugins=[DocDataAPIVersionPlugin()])

        # Setup the merchant soap object for use in all requests.
        self.merchant = self.client.factory.create('ns0:merchant')
        # TODO: Make this required if adapter is enabled (i.e. throw an error if not set instead of defaulting to dummy).
        self.merchant._name = getattr(settings, "DOCDATA_MERCHANT_NAME", 'dummy')
        self.merchant._password = getattr(settings, "DOCDATA_MERCHANT_PASSWORD", 'dummy')

        # TODO Work this out better.
        server = Site.objects.get_current().domain
        if server == 'localhost:8000':
            self.return_url = 'http://' + server + '#/support/thanks'
        else:
            self.return_url = 'https://' + server + '#/support/thanks'


    def get_payment_methods(self):
        return self.payment_methods


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
        paymentPreferences.profile = self.payment_methods[payment.payment_method_id]['profile'],
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
        # TODO No space allowed in postal code. Move to serializer?
        address.postalCode = payment.postal_code.replace(' ', '')
        address.city = payment.city

        country = self.client.factory.create('ns0:country')
        country._code = payment.country
        address.country = country

        billTo = self.client.factory.create('ns0:destination')
        billTo.address = address
        billTo.name = name

        if self.test:
            # A unique code for testing.
            payment.merchant_order_reference = str(timezone.now())
        else:
            # TODO: Make a setting for the prefix
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


    def create_webmenu_payment(self, payment):
        """ Return the Payment URL """

        if not payment.payment_method_id:
            raise DocDataPaymentException('ERROR', 'payment_method_id is not set')
        if not self.id_to_model_mapping[payment.payment_method_id] == DocDataWebMenu:
            raise DocDataPaymentException('ERROR',
                                          'payment_method_id {0} does not support WebMenu'.format(payment.payment_method_id))

        if not payment.payment_order_key:
            self.create_remote_payment_order(payment)

        params = {
            'payment_cluster_key': payment.payment_order_key,
            'merchant_name': self.merchant._name,
            'profile': self.payment_methods[payment.payment_method_id]['profile'],
            # TODO: Enable when have good URLs.
            # 'return_url_success': self.return_url,
            # 'return_url_pending': self.return_url,
            # 'return_url_canceled': self.return_url,
            # 'return_url_error': self.return_url,
            'client_language': payment.language,
            'default_pm': self.payment_methods[payment.payment_method_id]['id'],
        }

        if payment.payment_method_id == 'dd-ideal' and payment.payment_submethod_id:
            params['ideal_issuer_id'] = payment.payment_submethod_id
            params['default_act'] = 'true'

        if self.test:
            payment_url_base = 'https://test.docdatapayments.com/ps/menu'
        else:
            payment_url_base = 'https://secure.docdatapayments.com/ps/menu'

        # Create a DocDataWebMenu when we need it.
        webmenu_payment = payment.latest_payment_method
        if not webmenu_payment or not isinstance(webmenu_payment, DocDataWebMenu):
            webmenu_payment = DocDataWebMenu()
            webmenu_payment.docdata_payment_order = payment

        webmenu_payment.payment_url = payment_url_base + '?' + urlencode(params)
        webmenu_payment.save()
        return webmenu_payment.payment_url


    def map_status(self, status):
        # TODO: Translate the specific statuses into something generic we all understand
        return status
