# Based on: https://github.com/digitick/php-sepa-xml

from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring
from django.utils import timezone


class SepaFactory(object):
    """
    Create a SEPA xml for payments.

    """

    # boolean if true, the transaction will never be executed.
    is_test = False

    # string unambiguously identify the message.
    message_identification = None

    # string debtor's name.
    debtor_name = None

    # string debtor's account IBAN.
    debtor_iban = None

    # string Debtor's account bank BIC code.
    debtor_bic = None

    # string Debtor's account ISO currency code.
    currency = 'EUR'

    # string Payment sender's name.
    initiating_party_name = None

    # string Payment sender's ID (for example: the tax ID).
    initiating_party_id = None

    # string Unambiguously identify the payment.
    payment_info_id = None

    # string Purpose of the transaction(s).
    category_purpose_code = None

    # integer
    _header_control_sum_cents = 0

    # SepaCreditTransfer[]
    _credit_transfers = []

    # integer Number of payment transactions.
    _number_of_transactions = 0

    # string Payment method.
    _payment_method = 'TRF'

    # string Local service instrument code.
    _local_instrument_code = None

    # SimpleXMLElement
    _xml = None

    INITIAL_STRING = '<?xml version="1.0" encoding="UTF-8"?>' \
                     '<Document xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                     'xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"></Document>'

    def create(self, *args, **kwargs):
        """
        Set basic info.
        """

        self.is_test = getattr(kwargs, 'is_test', False)

        self.message_identification = str(kwargs['message_identification'])
        self.debtor_iban = kwargs['debtor_iban']
        self.debtor_bic = kwargs['debtor_bic']

        # For payments initiating_party is the debtor
        self.debtor_name = kwargs['initiating_party_name']

        self.initiating_party_name = kwargs['initiating_party_name']

        self.initiating_party_id = str(kwargs['initiating_party_id'])

        self.payment_info_id = str(kwargs['payment_info_id'])

    def as_xml(self):
        """ Return the XML string. """
        return tostring(self._generate_xml())

    def add_credit_transfer(self, *args, **kwargs):
        """ Add a credit transfer transaction. """
        transfer = SepaCreditTransfer()

        transfer.creditor_payment_id = kwargs['creditor_payment_id']
        transfer.amount = kwargs['amount']
        transfer.creditor_name = kwargs['creditor_name']
        transfer.creditor_iban = kwargs['creditor_iban']
        transfer.creditor_bic = kwargs['creditor_bic']

        transfer.end_to_end_id = str(self.message_identification) + '-' + str(self._number_of_transactions)

        transfer.currency = getattr(kwargs, 'currency', self.currency)
        transfer.remittance_information = getattr(kwargs, 'remittance_information', '')

        self._credit_transfers.append(transfer)
        self._number_of_transactions += 1
        self._header_control_sum_cents += transfer.amount

    def _generate_xml(self):
        """
        This were all is put together into an xml.
        """
        document = Element('Document')
        document.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        document.set('xmlns', 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03')

        self._main = SubElement(document, 'CstmrCdtTrfInitn')
        self._xml = document

        # Group Header
        grp_hdr = SubElement(self._main, 'GrpHdr')

        SubElement(grp_hdr, 'MsgId').text = str(self.message_identification)

        SubElement(grp_hdr, 'CreDtTm').text = timezone.datetime.strftime(timezone.now(), '%Y-%m-%mT%H:%I:%S')

        if self.is_test:
            prtry = SubElement(grp_hdr, 'Prtry').text = 'TEST'

        SubElement(grp_hdr, 'NbOfTxs').text = str(self._number_of_transactions)

        SubElement(grp_hdr, 'CtrlSum').text = self._int_to_currency(self._header_control_sum_cents)

        SubElement(grp_hdr, 'Grpg').text = 'SNGL'

        if self.initiating_party_id:
            initg_pty = SubElement(grp_hdr, 'InitgPty')
            SubElement(initg_pty, 'Nm').text = self.initiating_party_id

        # Credit Transfer Transaction Information
        # Rabobank wants only one transaction per payment info so we create multiple payment infos here.
        for transfer in self._credit_transfers:
            pmt_inf = SubElement(self._main, 'PmtInf')
            #pmt_inf.text = self.payment_info_id

            if self.category_purpose_code:
                cd = SubElement(pmt_inf, 'Cd')
                SubElement(cd, 'CtgyPurp').text = self.category_purpose_code

            SubElement(pmt_inf, 'PmtMtd').text = self._payment_method
            SubElement(pmt_inf, 'NbOfTxs').text = "1"
            #SubElement(pmt_inf, 'CtrlSum').text = self._int_to_currency(transfer.amount)

            pmt_tp_inf = SubElement(pmt_inf, 'PmtTpInf')
            svc_lvl = SubElement(pmt_tp_inf, 'SvcLvl')
            SubElement(svc_lvl, 'Cd').text = 'SEPA'

            if self._local_instrument_code:
                lcl_instr = SubElement(pmt_inf, 'LclInstr')
                SubElement(lcl_instr, 'Cd').text = self._local_instrument_code

            SubElement(pmt_inf, 'ReqdExctnDt').text = timezone.datetime.strftime(timezone.now(), '%Y-%m-%d')

            dbtr = SubElement(pmt_inf, 'Dbtr')
            SubElement(dbtr, 'Nm').text = self.debtor_name

            dbtr_acct = SubElement(pmt_inf, 'DbtrAcct')
            dbtr_id = SubElement(dbtr_acct, 'Id')
            SubElement(dbtr_id, 'IBAN').text = self.debtor_iban
            SubElement(dbtr_acct, 'Ccy').text = self.currency

            dbtr_agt = SubElement(pmt_inf, 'DbtrAgt')
            fin_isnstn_id = SubElement(dbtr_agt, 'FinInstnId')
            SubElement(fin_isnstn_id, 'BIC').text = self.debtor_bic

            SubElement(pmt_inf, 'ChrgBr').text = 'SLEV'

            amount = self._int_to_currency(transfer.amount)

            cd_trf_tx_inf = SubElement(pmt_inf, 'CdtTrfTxInf')

            pmt_id = SubElement(cd_trf_tx_inf, 'PmtId')
            SubElement(pmt_id, 'InstrId').text = transfer.transfer_id
            SubElement(pmt_id, 'EndToEndId').text = transfer.end_to_end_id

            amt = SubElement(cd_trf_tx_inf, 'Amt')
            instd_amt = SubElement(amt, 'InstdAmt', {'Ccy': transfer.currency})
            instd_amt.text = amount

            cdtr_agt = SubElement(cd_trf_tx_inf, 'CdtrAgt')
            fin_inst_id = SubElement(cdtr_agt, 'FinInstnId')
            bic = SubElement(fin_inst_id, 'BIC')
            bic.text = transfer.creditor_bic

            cdrt = SubElement(cd_trf_tx_inf, 'Cdtr')
            SubElement(cdrt, 'Nm').text = transfer.creditor_name

            cdtr_acct = SubElement(cd_trf_tx_inf, 'CdtrAcct')
            cdtr_id = SubElement(cdtr_acct, 'Id')
            SubElement(cdtr_id, 'IBAN').text = transfer.creditor_iban

            rmt_inf = SubElement(cd_trf_tx_inf, 'RmtInf')
            SubElement(rmt_inf, 'Ustrd').text = transfer.remittance_information

            SubElement(cd_trf_tx_inf, 'ChrgBr').text = 'SLEV'

        return self._xml

    def _int_to_currency(self, amount):
        """ Format an integer as a monetary value. """
        amount = Decimal(Decimal(amount) / 100)
        return "%.2f" % amount


class SepaCreditTransfer(object):
    """
    SEPA Credit Transfer Transaction Information.
    """

    # string Payment ID.
    transfer_id = None

    end_to_end_id = None

    currency = None
    creditor_bic = None
    creditor_name = None
    creditor_account_iban = None
    remittance_information = None
    amount = None
