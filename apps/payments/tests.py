from django.test import TestCase
from rest_framework import status


class SelectPaymentMethodIntegrationTest(TestCase):
    """
    Integration tests for the adding Donations to an Order (a cart in this case)
    """

    def setUp(self):
        self.payment_methods_url = '/i18n/api/payments/methods/'

    def show_payment_methods(self):
        """
        Tests for showing payment methods
        """

        # View a list of payment methods
        response = self.client.post(self.payment_methods_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
