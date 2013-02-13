from apps.cowry import factory, payments
from django.conf import settings
from django.test.testcases import TestCase
from django.utils import unittest
import requests
from requests.exceptions import ConnectionError


try:
    getattr(settings, 'DOCDATA_MERCHANT_NAME')
    getattr(settings, 'DOCDATA_MERCHANT_PASSWORD')
    requests.get('http://www.google.com')
    run_docdata_tests = True
except (ConnectionError, AttributeError):
    run_docdata_tests = False


class DocDataPaymentTests(TestCase):

    def setUp(self):
        if run_docdata_tests:
            self.payment = factory.create_payment_object('MASTERCARD', amount=2000, currency='EUR')
            self.payment.country = 'NL'
            self.payment.city = 'Amsterdam'
            self.payment.street = 'Dam'
            self.payment.postal_code = '1001AM'
            self.payment.first_name = 'Nijntje'
            self.payment.last_name = 'het Konijnje'
            self.payment.email = 'nijntje@hetkonijnje.nl'
            self.payment.save()
            payments.create_remote_payment_order(self.payment)

    @unittest.skipUnless(run_docdata_tests, 'DocData credentials not set or not online')
    def test_setup_payment(self):
        self.assertTrue(self.payment.payment_order_key)

    @unittest.skipUnless(run_docdata_tests, 'DocData credentials not set or not online')
    def test_setup_payment_url(self):
        payment_url = payments.get_payment_url(self.payment)
        response = requests.get(payment_url)
        self.assertEqual(response.status_code, 200)
