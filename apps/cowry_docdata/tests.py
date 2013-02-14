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

    @unittest.skipUnless(run_docdata_tests, 'DocData credentials not set or not online')
    def test_basic_payment(self):
        # Create the payment.
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

        # Check that the order key has been saved.
        self.assertTrue(self.payment.payment_order_key)

        # Test that the payment url works.
        payment_url = payments.get_payment_url(self.payment)
        response = requests.get(payment_url)
        self.assertEqual(response.status_code, 200)

    @unittest.skipUnless(run_docdata_tests, 'DocData credentials not set or not online')
    def test_payment_method_restrictions(self):
        # Test country restrictions.
        payment_method_ids = factory.get_payment_method_ids(country='NL')
        self.assertTrue('IDEAL' in payment_method_ids, "IDEAL not is in payment method list.")
        self.assertTrue(len(payment_method_ids) > 1, "Payment method list should have two or more payment methods.")
        payment_method_ids = factory.get_payment_method_ids(country='CA')
        self.assertTrue('IDEAL' not in payment_method_ids, "IDEAL should not be in payment method list.")

        # Test recurring restrictions.
        payment_method_ids = factory.get_payment_method_ids(recurring=True)
        self.assertTrue(len(payment_method_ids) == 0, "Payment method list should be empty.")
