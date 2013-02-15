from apps.cowry import factory, payments
from django.conf import settings
from django.test.testcases import TestCase
from django.utils import unittest
import requests
from requests.exceptions import ConnectionError
from rest_framework import status


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
        payment = factory.create_payment_object('dd-mastercard', amount=2000, currency='EUR')
        payment.country = 'NL'
        payment.city = 'Amsterdam'
        payment.street = 'Dam'
        payment.postal_code = '1001AM'
        payment.first_name = 'Nijntje'
        payment.last_name = 'het Konijnje'
        payment.email = 'nijntje@hetkonijnje.nl'
        payment.save()
        payments.create_remote_payment_order(payment)

        # Check that the order key has been saved.
        self.assertTrue(payment.payment_order_key)

        # Test that the payment url works.
        payment_url = payments.create_webmenu_payment(payment)
        response = requests.get(payment_url)
        self.assertEqual(response.status_code, 200)

        # Test the status changed notification.
        response = self.client.get('/i18n/api/ddscn/?mor={0}'.format(payment.merchant_order_reference))
        self.assertTrue(response.status_code, status.HTTP_200_OK)

    def test_payment_method_restrictions(self):
        # Test country restrictions.
        payment_method_ids = factory.get_payment_method_ids(country='NL')
        self.assertTrue('dd-ideal' in payment_method_ids, "dd-ideal not is in payment method list.")
        self.assertTrue(len(payment_method_ids) > 1, "Payment method list should have two or more payment methods.")
        payment_method_ids = factory.get_payment_method_ids(country='CA')
        self.assertTrue('dd-ideal' not in payment_method_ids, "dd-ideal should not be in payment method list.")

        # Test recurring restrictions.
        payment_method_ids = factory.get_payment_method_ids(recurring=True)
        self.assertTrue(len(payment_method_ids) == 0, "Payment method list should be empty.")
