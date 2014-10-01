import requests
from apps.cowry import factory, payments
from django.conf import settings
from django.test.testcases import TestCase
from django.test.utils import override_settings
from django.utils import unittest
from requests.exceptions import ConnectionError
from rest_framework import status
from .adapters import default_payment_methods


try:
    getattr(settings, 'COWRY_DOCDATA_MERCHANT_NAME')
    getattr(settings, 'COWRY_DOCDATA_TEST_MERCHANT_PASSWORD')
    requests.get('http://www.google.com')
    run_docdata_tests = True
except (ConnectionError, AttributeError):
    run_docdata_tests = False


@override_settings(COWRY_PAYMENT_METHODS=default_payment_methods)
class DocDataPaymentTests(TestCase):

    @unittest.skipUnless(run_docdata_tests, 'DocData credentials not set or not online')
    def test_basic_payment(self):
        # Create the payment.
        from apps.fund.models import Order
        order = Order.objects.create()
        order.save()
        payment = factory.create_payment_object(order, 'dd-webmenu', amount=2000, currency='EUR')
        payment.country = 'NL'
        payment.city = 'Amsterdam'
        payment.address = 'Dam'
        payment.postal_code = '1001AM'
        payment.first_name = 'Nijntje'
        payment.last_name = 'het Konijntje'
        payment.email = 'nijntje@hetkonijntje.nl'
        payment.save()
        payments.create_remote_payment_order(payment)

        # Check that the order key has been saved.
        self.assertTrue(payment.payment_order_id)

        # Test that the payment url works.
        payment_url = payments.get_payment_url(payment)
        response = requests.get(payment_url)
        self.assertEqual(response.status_code, 200)

        # Test the status changed notification.
        status_url = '/api/docdatastatuschanged/?order={0}'.format(payment.merchant_order_reference)
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_method_restrictions(self):
        # Test country restrictions.
        payment_method_ids = factory.get_payment_method_ids(country='NL')
        self.assertTrue('dd-ideal' in payment_method_ids, "dd-ideal not is in payment method list.")
        self.assertTrue(len(payment_method_ids) > 1, "Payment method list should have two or more payment methods.")
        payment_method_ids = factory.get_payment_method_ids(country='CA')
        self.assertTrue('dd-ideal' not in payment_method_ids, "dd-ideal should not be in payment method list.")

        # Test recurring restrictions.
        payment_method_ids = factory.get_payment_method_ids(recurring=True)
        self.assertTrue(len(payment_method_ids) == 1, "Payment method list should have one entry.")
