# Voucher code is disabled for now.
#
#import json
#from django.test import TestCase
#from rest_framework import status
#from apps.projects.tests import ProjectTestsMixin
#
#
#class VoucherApiIntegrationTest(ProjectTestsMixin, TestCase):
#     """
#     Integration tests for the adding Donations to an Order (a cart in this case)
#     """
#     def setUp(self):
#         self.some_project = self.create_project()
#         self.another_project = self.create_project()
#         self.some_user = self.create_user()
#         self.another_user = self.create_user()
#         self.current_vouchers_url = '/api/fund/orders/current/vouchers/'
#         self.vouchers_url = '/api/fund/vouchers/'
#         self.current_order_url = '/api/fund/orders/current'
#         self.some_voucher_data = {
#             'amount': 25, 'text': 'Look at this!',
#             'receiver_name': 'Bart', 'receiver_email': 'bart@1procentclub.nl',
#             'sender_name': 'Webmaster', 'sender_email': 'webmaster@1procentclub.nl'
#         }
#         self.another_voucher_data = {
#             'amount': 50, 'receiver_email': 'you@1procentclub.nl', 'sender_email': 'me@1procentclub.nl'
#         }
#
#     def test_current_order_voucher_crud(self):
#         """
#         Tests for creating, retrieving, updating and deleting a voucher to shopping cart.
#         """
#         # First make sure we have a current order
#         self.client.login(username=self.some_user.email, password='testing')
#         response = self.client.get(self.current_order_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
#         self.assertEqual(response.data['status'], 'current')
#
#         # Create a Voucher.
#         response = self.client.post(self.current_vouchers_url, self.some_voucher_data)
#         some_voucher_detail_url = '{0}{1}'.format(self.current_vouchers_url, response.data['id'])
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
#         self.assertEqual(response.data['amount'], '25.00')
#         self.assertEqual(response.data['receiver_name'], self.some_voucher_data['receiver_name'])
#         self.assertEqual(response.data['status'], 'new')
#
#         # Create another voucher.
#         response = self.client.post(self.current_vouchers_url, self.another_voucher_data)
#         another_voucher_detail_url = '{0}{1}'.format(self.current_vouchers_url, response.data['id'])
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
#         self.assertEqual(response.data['amount'], '50.00')
#         self.assertEqual(response.data['receiver_email'], self.another_voucher_data['receiver_email'])
#         self.assertEqual(response.data['status'], 'new')
#
#         # Check that the order now holds that two vouchers.
#         response = self.client.get(self.current_order_url)
#         self.assertEqual(response.data['total'], '75.00')
#         response = self.client.get(self.current_vouchers_url)
#         self.assertEqual(len(response.data['results']), 2)
#
#         # Remove the first voucher and see if all is updated correctly.
#         response = self.client.delete(some_voucher_detail_url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         response = self.client.get(self.current_order_url)
#         self.assertEqual(response.data['total'], '50.00')
#         response = self.client.get(self.current_vouchers_url)
#         self.assertEqual(len(response.data['results']), 1)
#
#         # Setting 77 as amount should fail
#         self.some_voucher_data['amount'] = 77
#         response = self.client.post(self.current_vouchers_url, self.some_voucher_data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
#
#         # Sending a status should not be saved
#         self.some_voucher_data['amount'] = 10
#         self.some_voucher_data['status'] = 'paid'
#         response = self.client.post(self.current_vouchers_url, self.some_voucher_data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
#         self.assertEqual(response.data['amount'], '10.00')
#         self.assertEqual(response.data['receiver_email'], self.some_voucher_data['receiver_email'])
#         self.assertEqual(response.data['status'], 'new')
#
#         # Updating the amount on a voucher is fine
#         self.another_voucher_data['amount'] = 100
#         response = self.client.put(another_voucher_detail_url, json.dumps(self.another_voucher_data), 'application/json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
#         self.assertEqual(response.data['amount'], '100.00')
#
#         self.some_voucher_data['receiver_email'] = 'not good'
#         self.some_voucher_data['sender_email'] = None
#         response = self.client.post(self.current_vouchers_url, self.some_voucher_data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
#
