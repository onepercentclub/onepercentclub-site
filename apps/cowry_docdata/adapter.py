import hashlib
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.http import urlencode
from xml.dom import minidom
from lxml import etree
from cowry.utils import urlopen
from cowry.adapter import AbstractPaymentAdapter
from .models import DocdataPaymentInfo
from django.utils import timezone


class DocdataPaymentAdapter(AbstractPaymentAdapter):
    """
        Docdata payments
    """

    test_url = 'https://test.tripledeal.com/ps/com.tripledeal.paymentservice.servlets.PaymentService'
    live_url = 'https://www.tripledeal.com/ps/com.tripledeal.paymentservice.servlets.PaymentService'

    # New Docdata API
    new_test_url = 'https://test.tripledeal.com/ps/services/paymentservice/0_9'

    return_url = None

    url = None

    def __init__(self, debug=True):
        self.merchant_name = getattr(settings, "DOCDATA_MERCHANT_NAME", 'dummy')
        self.merchant_password = getattr(settings, "DOCDATA_MERCHANT_PASSWORD", 'dummy')
        server = Site.objects.get_current().domain
        if server == 'localhost:8000':
            self.return_url = 'http://' + server + '#/support/thanks'
        else:
            self.return_url = 'https://' + server + '#/support/thanks'
        if debug:
            self.url = self.test_url
        else:
            self.url = self.live_url


    def create_payment_cluster(self):
        """
        Create a PaymentCluster based on PaymentProcess values
        A PaymentCluster is needed to talk to the Docdata API

        """
        if not self.payment_info:
            raise Exception("PaymentProcess not set.")

        params = self.instance_dict(self.payment_process)

        # Set the command to create a payment cluster
        params['command'] = 'new_payment_cluster'

        # Raises URLError on errors.
        result = urlopen(self.url, urlencode(params))

        # Parse the result XML
        resultdom = minidom.parse(result)

        # Check for errors
        self._check_errors(resultdom)

        # Get cluster key and id
        id = resultdom.getElementsByTagName('id')[0].getAttribute('value')
        key = resultdom.getElementsByTagName('key')[0].getAttribute('value')

        self.payment_cluster = {'id':id, 'key':key}

        return self.payment_cluster


    def _check_errors(self, resultdom):
        """ Check for errors in the DOM, raise PaymentException if found. """

        errors = resultdom.getElementsByTagName('errorlist').item(0)
        if errors:
            error_list = []
            for error in errors.getElementsByTagName('error'):
                error_list.append(error.getAttribute('msg'))

            raise Exception('Something went wrong!', error_list)


    def create_payment_info(self, *args, **kwargs):
        """
            Create a PaymentProcess based on a Payment and 
            the returned form
        """

        # TODO: load these values dynamically??
        amount = kwargs['amount']
        currency = 'EUR'
        profile = 'standard'
        language = 'en',
        days_pay_period = 5
        
        # TODO: member_id here (if available)
        client_id = 1
        # TODO: Make a decent transaction ID here.
        transaction_id = '1PC-' + str(timezone.now())

        if self.get_payment().payment_info:
            self.payment_info = self.get_payment().payment_info
        else:
            self.payment_info = DocdataPaymentInfo.objects.create(amount=amount)

        self.payment_info.transaction_id = transaction_id
        self.payment_info.client_id = 1
        self.payment_info.client_email = kwargs.get('email', '')
        self.payment_info.client_firstname = kwargs.get('first_name', '')
        self.payment_info.client_lastname = kwargs.get('last_name', '')
        self.payment_info.client_address = kwargs.get('address', '')
        self.payment_info.client_zip = kwargs.get('zip_code', '')
        self.payment_info.client_city = kwargs.get('city', '')
        self.payment_info.client_country = kwargs.get('country', '')

        cluster = self.new_payment_cluster(
            merchant_name = self.merchant_name,
            merchant_password = self.merchant_password,
            merchant_transaction_id = transaction_id,
            profile = profile,

            price = amount,
            cur_price = currency,

            client_id = client_id,
            client_email = kwargs.get('email', ''),
            client_firstname = kwargs.get('first_name'),
            client_lastname = kwargs.get('last_name'),
            client_address = kwargs.get('address'),
            client_zip = kwargs.get('zip_code'),
            client_city = kwargs.get('city'),
            client_country = kwargs.get('country'),

            client_language = 'en',
            days_pay_period = days_pay_period
        )
        self.payment_info.payment_cluster_id = cluster['payment_cluster_id']
        self.payment_info.payment_cluster_key = cluster['payment_cluster_key']
        self.payment_info.payment_url = self.get_payment_url()
        self.payment_info.save()

        return self.payment_info

    
    def get_payment_url(self):
        """ Return the Payment URL """

        payment = self.get_payment()
        
        # Set the parameters to generate the return url
        debug_webmenu_params = {
            'command': 'show_payment_cluster',
            'merchant_name': self.merchant_name,
            'payment_cluster_key': self.payment_info.payment_cluster_key,

            'return_url_success': self.return_url,
            'return_url_canceled': self.return_url,
            'return_url_pending': self.return_url

        }

        # Forward to DirectDebit input @ Docdata (Works!)
        debug_direct_debit_params = {
            'command': 'show_payment_cluster',
            'merchant_name': self.merchant_name,
            'payment_cluster_key': self.payment_info.payment_cluster_key,

            'payment_method': 'directdebitnc-online-nl',
            'default_pm': 'directdebitnc-online-nl',
            'default_act': 'Y',

            'return_url_success': self.return_url,
            'return_url_canceled': self.return_url,
            'return_url_pending': self.return_url

        }

        # Forward to Mastercard input @ Docdata (Works!)
        debug_mastercard_params = {
            'command': 'show_payment_cluster',
            'merchant_name': self.merchant_name,
            'payment_cluster_key': self.payment_info.payment_cluster_key,

            'default_pm': 'tripledeal-ipaygwv2-mc-ssl',
            'default_act': 'Y',

            'return_url_success': self.return_url,
            'return_url_canceled': self.return_url,
            'return_url_pending': self.return_url

        }

        self.payment_info.payment_url = self.url+'?'+urlencode(debug_webmenu_params)
            
        return self.payment_info.payment_url


    def get_direct_payment_url(self):

        payment = self.get_payment()

        """ Return the URL for show_payment_cluster. """
        # Set the parameters to generate the return url
        debug_direct_debit_params = {
            'command': 'start_partial_payment',
            'merchant_name': self.merchant_name,
            'merchant_password': self.merchant_password,
            'report_type': 'xml_all',
            'payment_cluster_key': self.payment_info.payment_cluster_key,
            'payment_method': 'direct-directdebitnc2-online-nl',

            'client_holder_fullname' : 'Malle Eppie',
            'client_holder_city' : 'Lelijkstad',
            'client_holder_account_nt' : '123456789',

            #'return_url_success': 'http://localhost:8000/i18n/api/fund/payments/final',
            #'return_url_canceled': 'http://localhost:8000/i18n/api/fund/payments/final',
            #'return_url_pending': 'http://localhost:8000/i18n/api/fund/payments/final'

        }

        debug_transfer_params = {
            'command': 'start_partial_payment',
            'merchant_name': self.merchant_name,
            'merchant_password': self.merchant_password,
            'report_type': 'xml_all',
            'payment_cluster_key': self.payment_info.payment_cluster_key,
            'payment_method': 'direct-bank-transfer-nl',

            'return_url_success': self.return_url,
            'return_url_canceled': self.return_url,
            'return_url_pending': self.return_url

        }

        debug_ideal_params = {
            'command': 'start_partial_payment',
            'merchant_name': self.merchant_name,
            'merchant_password': self.merchant_password,
            'report_type': 'xml_all',
            'payment_cluster_key': self.payment_info.payment_cluster_key,
            'payment_method': 'ideal-ing-1procentclub_nl',

            'return_url_success': self.return_url,
            'return_url_canceled': self.return_url,
            'return_url_pending': self.return_url

        }

        result = urlopen(self.url, urlencode(debug_direct_debit_params))

        print self.url + '?' + urlencode(debug_direct_debit_params)
        print result.getvalue()

        # Check for errors
        resultdom = minidom.parse(result)
        self._check_errors(resultdom)

        xml = etree.fromstring(result.getvalue())

        url = xml.findall('.//payment_cluster_process')[0].text


        self.payment_info.payment_url = url

        self.payment_info.save()

        return self.payment_info.payment_url


    def check_payment_info(self):

        # Available report_type's
        # 'txt_simple', 'txt_simple2', 'xml_std', 'xml_ext','xml_all'

        self.payment_info = self.payment.payment_info

        params = {
            'command': 'status_payment_cluster',
            'merchant_name': self.merchant_name,
            'merchant_password': self.merchant_password,
            'payment_cluster_key': self.payment_info.payment_cluster_key,
            'report_type': 'xml_all'
        }

        # Raises URLError on errors.
        result = urlopen(self.url, urlencode(params))

        # Parse the result XML

        xml = etree.fromstring(result.getvalue())
        status = xml.findall('.//payment_cluster_process')[0].text
        
        self.payment_info.status = self.map_status(status)

        self.payment_info.save()

        return self.payment


    def map_status(self, status):
        # TODO: Translate the specific statuses into something generic we all understand
        return status

    def new_payment_cluster(self, **kwargs):
        """
            Create a DocData PaymenClustere needed to send 
            commands to their API.
        """
         
         # Check if we have all params we need
        assert 'merchant_name' in kwargs
        assert 'merchant_password' in kwargs
        assert 'merchant_transaction_id' in kwargs
        assert 'profile' in kwargs
        assert 'price' in kwargs
        assert 'cur_price' in kwargs

        assert 'client_id' in kwargs
        assert 'client_email' in kwargs
        assert 'client_firstname' in kwargs
        assert 'client_lastname' in kwargs
        assert 'client_address' in kwargs
        assert 'client_zip' in kwargs
        assert 'client_city' in kwargs
        assert 'client_country' in kwargs
        assert 'client_language' in kwargs
        assert 'days_pay_period' in kwargs
        
        """ 
            Optional values:
            
            description
            days_exhortation1
            profile_exhortation1
            days_exhortation2
            profile_exhortation2
            css_id
            template_nr 
            client_company 
            receipt_text 
            include_costs 
            cancellable
            force_country 
            var1
            ..
            varn 
        """
        
        # Set the command to create a payment cluster
        kwargs['command'] = 'new_payment_cluster'
        
        # Raises URLError on errors.
        result = urlopen(self.url, urlencode(kwargs))

        # Parse the result XML
        resultdom = minidom.parse(result)

        # Check for errors
        self._check_errors(resultdom)

        # Get cluster key and id
        id = resultdom.getElementsByTagName('id')[0].getAttribute('value')
        key = resultdom.getElementsByTagName('key')[0].getAttribute('value')

        self.payment_cluster_id = id
        self.payment_cluster_key = key
        return {'payment_cluster_id': id, 'payment_cluster_key':key}




