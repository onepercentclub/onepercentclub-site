import os
import unittest
import decimal

from lxml import etree

from apps.sepa.sepa import SepaAccount, SepaDocument
from .base import SepaXMLTestMixin


class ExampleXMLTest(SepaXMLTestMixin, unittest.TestCase):
    """ Attempt to test recreating an example XML file """

    def setUp(self):
        super(ExampleXMLTest, self).setUp()

        # Read and validate example XML file
        example_file = os.path.join(
            self.directory, 'BvN-pain.001.001.03-example-message.xml'
        )
        self.example = etree.parse(example_file)

        self.xmlschema.assertValid(self.example)

    def test_generate_example(self):
        """ Attempt to recreate example XML file. """
        pass


class CalculateMoneyDonatedTests(SepaXMLTestMixin, unittest.TestCase):
    """
    Generate and attempt to validate an XML file modelled after actual
    transactions
    """

    def setUp(self):
        super(CalculateMoneyDonatedTests, self).setUp()

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
            'amount': decimal.Decimal('50.00'),
            'id': 'PAYMENT 1253675',
            'remittance_info': 'some info'
        }

        self.payment2 = {
            'amount': decimal.Decimal('25.00'),
            'id': 'PAYMENT 234532',
            'remittance_info': 'my info'
        }

        self.message_id = 'BATCH-1234'
        payment_id = 'PAYMENTS TODAY'

        # Create base for SEPA
        sepa = SepaDocument(type='CT')
        sepa.set_info(message_identification=self.message_id, payment_info_id=payment_id)
        sepa.set_initiating_party(name=self.some_account['name'], id=self.some_account['id'])

        some_account = SepaAccount(name=self.some_account['name'], iban=self.some_account['iban'],
                                   bic=self.some_account['bic'])
        sepa.set_debtor(some_account)

        # Add a payment
        another_account = SepaAccount(name=self.another_account['name'], iban=self.another_account['iban'],
                                      bic=self.another_account['bic'])

        sepa.add_credit_transfer(creditor=another_account, amount=self.payment1['amount'],
                                 creditor_payment_id=self.payment1['id'],
                                 remittance_information=self.payment1['remittance_info'])

        # Add another payment
        third_account = SepaAccount(name=self.third_account['name'], iban=self.third_account['iban'],
                                    bic=self.third_account['bic'])
        sepa.add_credit_transfer(creditor=third_account, creditor_payment_id=self.payment2['id'],
                                 amount=self.payment2['amount'],
                                 remittance_information=self.payment2['remittance_info'])

        # Now lets get the xml for these payments
        self.xml = sepa.as_xml()

    def test_parse_xml(self):
        """ Test parsing the generated XML """

        # Still no errors? Lets check the xml.
        tree = etree.XML(self.xml)

        main = tree[0]

        self.assertEqual(main.tag,
            '{urn:iso:std:iso:20022:tech:xsd:pain.001.001.03}CstmrCdtTrfInitn'
        )

        header = main[0]

        self.assertEqual(header.tag,
            '{urn:iso:std:iso:20022:tech:xsd:pain.001.001.03}GrpHdr')
        self.assertEqual(header[0].text, self.message_id)

        # We should have two payments
        self.assertEqual(header[2].text, "2")

        # Total amount should be the sum of two payments coverted to euros
        self.assertEqual(header[3].text, '75.00')

        # Now lets check The second payment IBANs
        second_payment = main[2]

        namespaces = {
            # Default
            'pain': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        self.assertEqual(
            second_payment.find(
                'pain:DbtrAcct/pain:Id/pain:IBAN', namespaces=namespaces
            ).text,
            self.some_account['iban']
        )

        self.assertEqual(
            second_payment.find(
                'pain:CdtTrfTxInf/pain:CdtrAcct/pain:Id/pain:IBAN', namespaces=namespaces
            ).text,
            self.third_account['iban']
        )

    def test_validate_xml(self):
        """ Assert the XML is valid according to schema """

        tree = etree.XML(self.xml)
        self.xmlschema.assertValid(tree)
