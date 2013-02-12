from apps.cowry import factory, payments
from django.test.testcases import TestCase
import requests


# TODO Only run these tests when online and the merchant account / password is set.
class DocDataPaymentTests(TestCase):

    def setUp(self):
        self.payment = factory.create_payment_object('MASTERCARD', 2000, 'EUR')
        self.payment.country = 'NL'
        self.payment.city = 'Amsterdam'
        self.payment.street = 'Dam Square'
        self.payment.house_number = "N/A"
        self.payment.postal_code = '1001AM'
        self.payment.first_name = 'Nijntje'
        self.payment.last_name = 'het Konijnje'
        self.payment.email = 'nijntje@hetkonijnje.nl'
        self.payment.save()
        payments.create_remote_payment_order(self.payment)

    def test_setup_payment(self):
        self.assertTrue(self.payment.payment_order_key)

    def test_setup_payment_url(self):
        payment_url = payments.get_payment_url(self.payment)
        response = requests.get(payment_url)
        self.assertEqual(response.status_code, 200)
