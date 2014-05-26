# Based on: https://github.com/digitick/php-sepa-xml
# This app will take information for several payments and create a SEPA xml file for internet banking.
# It takes specifics for Rabobank (The Netherlands)
# https://www.rabobank.com/en/images/SEPA%20Credit%20Transfer%20format%20description%20v1.0.pdf

import decimal

from django.utils.timezone import datetime

from lxml.etree import Element, SubElement, tostring


class CreditTransfer(object):
    """
    SEPA Credit Transfer Transaction Information.
    """

    end_to_end_id = None

    currency = None
    creditor = None
    remittance_information = None
    amount = None


class DirectDebit(object):
    """
    SEPA (Direct) Debit Transfer Transaction Information.
    """

    end_to_end_id = None

    currency = None
    debtor_bic = None
    debtor_name = None
    debtor_account_iban = None
    debit_information = None
    aUnnamedmount = None


class InitiatingParty(object):

    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']


class SepaAccount(object):
    """
    A Bank Account. Can be debtor or creditor.
    """

    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']
        self.iban = kwargs['iban']
        self.bic = kwargs['bic']


class SepaDocument(object):
    """
    Create a SEPA xml for payments.

    """

    # If true, the transaction will never be executed.
    is_test = False

    # Unambiguously identify the message.
    message_identification = None

    # Unambiguously identify the payment.
    payment_info_id = None

    # Debtor's account ISO currency code.
    currency = 'EUR'

    # Total amount of all transactions
    _header_control_sum = decimal.Decimal('0.00')

    # Array to hold the transfers
    _credit_transfers = []
    _direct_debits = []

    # Payment method.
    _type = 'CT'  # CT: Credit transfer, DD: Direct debit
    _payment_method = 'TRF'

    # Purpose of the transaction(s).
    category_purpose_code = None

    # string Local service instrument code.
    _local_instrument_code = None


    # For: Future direct debit reference
    # LclInstrm/Cd: CORE
    # SeqTp: FRST / RCUR


    # XML
    _xml = None

    def __init__(self, type='CT', *args, **kwargs):
        """
        Set transaction type.
        DD: Direct Debit
        CT: Credit Transfer
        """
        self._type = type


    def set_initiating_party(self, *args, **kwargs):
        self.initiating_party = InitiatingParty(**kwargs)

    def set_info(self, *args, **kwargs):
        self.payment_info_id = str(kwargs['payment_info_id'])
        self.message_identification = str(kwargs['message_identification'])

    def set_debtor(self, debtor):
        """ Add a credit transfer transaction. """
        if self._type != 'CT':
            raise Exception("Can only set a debtor to Sepa Document of type CT")
        if not isinstance(debtor, SepaAccount):
            raise Exception("Debtor should be of type SepaAccount")
        self.debtor = debtor

    def set_creditor(self, creditor):
        if self._type != 'DD':
            raise Exception("Can only set a creditor to Sepa Document of type DD")
        if not isinstance(creditor, SepaAccount):
            raise Exception("Creditor should be of type SepaAccount")
        self.creditor = creditor

    def as_xml(self):
        """ Return the XML string. """
        return tostring(self._generate_xml(),
            xml_declaration=True, encoding='UTF-8', pretty_print=True)

    def get_header_control_sum(self):
        """ Get the header control sum in cents """
        return self._header_control_sum

    def add_direct_debit(self, *args, **kwargs):
        """ Add a direct debit transaction. """
        if self._type != 'DD':
            raise Exception("Can only add a direct debit to Sepa Document of type DD")

        transfer = DirectDebit()

        transfer.creditor_payment_id = kwargs['creditor_payment_id']

        transfer.amount = decimal.Decimal(kwargs['amount'])

        transfer.creditor = kwargs['creditor']

        transfer.end_to_end_id = str(self.message_identification) + '-' + str(len(self._credit_transfers))

        transfer.currency = getattr(kwargs, 'currency', self.currency)
        transfer.remittance_information = getattr(kwargs, 'remittance_information', '')

        self._credit_transfers.append(transfer)
        self._header_control_sum += transfer.amount

    def add_credit_transfer(self, *args, **kwargs):
        """ Add a credit transfer transaction. """
        if self._type != 'CT':
            raise Exception("Can only add a credit transfer to Sepa Document of type CT")

        transfer = CreditTransfer()

        transfer.creditor_payment_id = kwargs['creditor_payment_id']
        transfer.amount = decimal.Decimal(kwargs['amount'])
        transfer.creditor = kwargs['creditor']

        transfer.end_to_end_id = str(self.message_identification) + '-' + str(len(self._credit_transfers))

        transfer.currency = getattr(kwargs, 'currency', self.currency)
        transfer.remittance_information = getattr(kwargs, 'remittance_information', '')

        self._credit_transfers.append(transfer)
        self._header_control_sum += transfer.amount

    def _generate_xml(self):
        """
        This were all is put together into an xml.
        """
        namespaces = {
            # Default
            None: 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        document = Element('Document', nsmap=namespaces)

        if self._type is 'CT':
            main = SubElement(document, 'CstmrCdtTrfInitn')
        elif self._type is 'DD':
            main = SubElement(document, 'CstmrDrctDbtInitn')
        else:
            raise Exception('Unknown SepaDocument type, or type not set.')

        # Group Header
        grp_hdr = SubElement(main, 'GrpHdr')

        SubElement(grp_hdr, 'MsgId').text = str(self.message_identification)

        SubElement(grp_hdr, 'CreDtTm').text = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%I:%S')

        SubElement(grp_hdr, 'NbOfTxs').text = str(len(self._credit_transfers))

        SubElement(grp_hdr, 'CtrlSum').text = str(self._header_control_sum)

        assert self.initiating_party
        initg_pty = SubElement(grp_hdr, 'InitgPty')
        SubElement(initg_pty, 'Nm').text = self.initiating_party.name

        # Credit Transfer Transactions Information
        # Rabobank wants only one transaction per payment info so we create multiple payment infos here.
        for transfer in self._credit_transfers:
            # PaymentInformation
            pmt_inf = SubElement(main, 'PmtInf')

            # PaymentInformationIdentification
            # PmtInfId
            SubElement(pmt_inf, 'PmtInfId').text = transfer.creditor_payment_id

            if self.category_purpose_code:
                cd = SubElement(pmt_inf, 'Cd')
                SubElement(cd, 'CtgyPurp').text = self.category_purpose_code

            # PaymentMethod
            SubElement(pmt_inf, 'PmtMtd').text = self._payment_method

            # BatchBooking [optional]
            # BtchBookg

            # NumberofTransactions
            SubElement(pmt_inf, 'NbOfTxs').text = "1"

            # ControlSum [optional]
            # CtrlSum

            # PaymentTypeInformation
            pmt_tp_inf = SubElement(pmt_inf, 'PmtTpInf')

            # InstructionPriority [optional]
            # InstrPrty

            # ServiceLevel
            svc_lvl = SubElement(pmt_tp_inf, 'SvcLvl')

            # Code
            SubElement(svc_lvl, 'Cd').text = 'SEPA'

            if self._local_instrument_code:
                # LocalInstrument
                lcl_instr = SubElement(pmt_inf, 'LclInstr')

                # Code
                SubElement(lcl_instr, 'Cd').text = self._local_instrument_code

                # Proprietary [otional]
                # Prtry

            # CategoryPurpose [optional
            # CtgyPurp
            #
            #  - Cd Code
            #  - Prtry Proprietary

            # RequestedExecutionDate
            SubElement(pmt_inf, 'ReqdExctnDt').text = datetime.strftime(datetime.now(), '%Y-%m-%d')

            # Debtor
            dbtr = SubElement(pmt_inf, 'Dbtr')

            # Name
            SubElement(dbtr, 'Nm').text = self.debtor.name

            # PostalAddress [optional]
            # PstlAdr
            #
            # - Country [optional]
            # - Ctry
            #
            # - AddressLine [optional]
            # - AdrLine

            # Identification [optional]
            # Id

            # DebtorAccount
            dbtr_acct = SubElement(pmt_inf, 'DbtrAcct')

            # Identification
            dbtr_id = SubElement(dbtr_acct, 'Id')

            # IBAN
            SubElement(dbtr_id, 'IBAN').text = self.debtor.iban

            # Currency
            SubElement(dbtr_acct, 'Ccy').text = self.currency

            # DebtorAgent
            dbtr_agt = SubElement(pmt_inf, 'DbtrAgt')

            # FinancialInstitutionIdentification
            fin_isnstn_id = SubElement(dbtr_agt, 'FinInstnId')

            # BIC
            SubElement(fin_isnstn_id, 'BIC').text = self.debtor.bic

            # UltimateDebtor [optional]
            # UltmtDbtr
            # - Name
            # - Nm
            #
            # - Identification
            # - Id

            # ChargeBearer
            SubElement(pmt_inf, 'ChrgBr').text = 'SLEV'

            # CTTransactionInformation
            cd_trf_tx_inf = SubElement(pmt_inf, 'CdtTrfTxInf')

            # PaymentIdentification
            pmt_id = SubElement(cd_trf_tx_inf, 'PmtId')

            # InstructionIdentification
            # InstrId [optional]

            # End to End Identification
            SubElement(pmt_id, 'EndToEndId').text = transfer.end_to_end_id

            # PaymentTypeInformation [optional]
            # PmtTpInf

            # ServiceLevel
            # SvcLvl [optional]
            #
            # - Code
            # - Cd

            # LocalInstrument [optional]
            # LclInstrm
            #
            # - Code
            # - Cd
            #
            # - Proprietary
            # - Prtry

            # CategoryPurpose [optional]
            # CtgyPurp
            #
            # - Code
            # - Cd

            # Amount
            amt = SubElement(cd_trf_tx_inf, 'Amt')

            # InstructedAmount
            instd_amt = SubElement(amt, 'InstdAmt', {'Ccy': transfer.currency})
            instd_amt.text = str(transfer.amount)

            # Charge Bearer [optional]
            # ChrgBr

            # UltimateDebtor [optional]
            # UltmtDbtr
            # - Name
            # - Nm
            #
            # - Identification
            # - Id

            # Creditor Agent
            cdtr_agt = SubElement(cd_trf_tx_inf, 'CdtrAgt')

            # FinancialInstitutionIdentification
            fin_inst_id = SubElement(cdtr_agt, 'FinInstnId')

            # BIC
            bic = SubElement(fin_inst_id, 'BIC')
            bic.text = transfer.creditor.bic

            # Creditor
            cdrt = SubElement(cd_trf_tx_inf, 'Cdtr')

            # Name
            SubElement(cdrt, 'Nm').text = transfer.creditor.name

            # PostalAddress [optional]
            # PstlAdr
            #
            # - Country [optional]
            # - Ctry
            #
            # - AddressLine [optional]
            # - AdrLine

            # Identification [optional]
            # Id

            # Creditor Account
            cdtr_acct = SubElement(cd_trf_tx_inf, 'CdtrAcct')

            # Id
            cdtr_id = SubElement(cdtr_acct, 'Id')

            # IBAN
            SubElement(cdtr_id, 'IBAN').text = transfer.creditor.iban

            # Currency [optional]
            # Ccy

            # Name [optional]
            # Nm

            # UltimateDebtor [optional]
            # UltmtDbtr
            # - Name
            # - Nm
            #
            # - Identification
            # - Id

            # Purpose [optional]
            # Purp
            #
            # - Code
            # - Cd

            # RemittanceInformation
            rmt_inf = SubElement(cd_trf_tx_inf, 'RmtInf')

            # Unstructured
            if transfer.remittance_information:
                SubElement(rmt_inf, 'Ustrd').text = transfer.remittance_information

            # Structured (optional)
            #
            # - CreditorReferenceInformation (optional)
            #
            # - - Type
            # - - Tp
            #
            # - - - CodeOrProprietary
            # - - - CdOrPrtry
            # - - - - Code
            # - - - Issuer
            # - - Reference

        return document
