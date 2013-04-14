from django.test import TestCase
from xml.etree import ElementTree
from sepa import SepaDocument


class CalculateMoneyDonatedTest(TestCase):

    def setUp(self):
        self.some_account = {
            'name': '1%CLUB',
            'iban': 'NL45RABO0132207044',
            'bic': 'RABONL2U',
            'id': 'A01'
        }

        self.another_account = {
            'name': 'Nice Project',
            'iban': 'NL13TEST0123456789',
            'bic': 'TESTNL2A',
            'id': 'P551'
        }

        self.third_account = {
            'name': 'SHO',
            'iban': 'NL28INGB0000000777',
            'bic': 'INGBNL2A',
            'id': 'P345'
        }

        self.payment1 = {
            'amount': 500000,
            'id': 'PAYMENT 1253675',
            'remittance_info': 'some info'
        }

        self.payment2 = {
            'amount': 75000,
            'id': 'PAYMENT 234532',
            'remittance_info': 'my info'
        }

    def test_payments_sepa(self):

        message_id = 'BATCH-1234'
        payment_id = 'PAYMENTS TODAY'

        # Create base for SEPA
        sepa = SepaDocument(message_identification=message_id, debtor_name=self.some_account['name'],
                    debtor_iban=self.some_account['iban'], debtor_bic=self.some_account['bic'],
                    initiating_party_name=self.some_account['name'], initiating_party_id=self.some_account['id'],
                    payment_info_id=payment_id)

        # Add a payment
        sepa.add_credit_transfer(creditor_name=self.another_account['name'], creditor_iban=self.another_account['iban'],
                                 creditor_bic=self.another_account['bic'],
                                 creditor_payment_id=self.payment1['id'], amount=self.payment1['amount'],
                                 remittance_information=self.payment1['remittance_info'])

        # Add another payment
        sepa.add_credit_transfer(creditor_name=self.third_account['name'], creditor_iban=self.third_account['iban'],
                                 creditor_bic=self.third_account['bic'],
                                 creditor_payment_id=self.payment2['id'], amount=self.payment2['amount'],
                                 remittance_information=self.payment2['remittance_info'])

        # Now lets get the xml for these payments
        xml = sepa.as_xml()

        # Still no errors? Lets check the xml.
        tree = ElementTree.XML(xml)

        self.assertEqual(tree[0][0][0].text, message_id)

        # We should have two payments
        self.assertEqual(tree[0][0][2].text, "2")

        # Total amount should be the sum of two payments coverted to euros
        total = self.payment1['amount'] + self.payment2['amount']
        total = "%.2f" % (total / 100)
        self.assertEqual(tree[0][0][3].text, total)

        # Now lets check The second payment IBANs
        self.assertEqual(tree[0][2][5][0][0].text, self.some_account['iban'])
        self.assertEqual(tree[0][2][8][4][0][0].text, self.third_account['iban'])
