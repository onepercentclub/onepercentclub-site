import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.csvimport.forms import CSVImportForm

from .dialects import DocdataDialect


class BankTransactionImportForm(CSVImportForm):
    """ Import form for bank transactions. """

    # Map field names or numbers to database fields
    field_mapping = {
        0: 'sender_account',
        1: 'currency',
        2: 'interest_date',
        3: 'credit_debit',
        4: 'amount',
        5: 'counter_account',
        6: 'counter_name',
        7: 'book_date',
        8: 'book_code',
        9: 'filler',
        10: 'description1',
        11: 'description2',
        12: 'description3',
        13: 'description4',
        14: 'description5',
        15: 'description6',
        16: 'end_to_end_id',
        17: 'id_recipient',
        18: 'mandate_id'
    }

    def _reformat_date(self, date):
        assert len(date) == 8
        return datetime.datetime.strptime(date, '%Y%m%d').date()

    def pre_save(self, instance):
        # Fixup date after raw CSV import.
        instance.interest_date = self._reformat_date(instance.interest_date)
        instance.book_date = self._reformat_date(instance.book_date)

    def validate_csv(self, reader):
        """ Make sure there is no date overlap in CSV. """
        # Discard header
        reader.next()

        for row in reader:
            book_date = self._reformat_date(row[7])

            if self.model.objects.filter(book_date=book_date).exists():
                raise forms.ValidationError(
                    _(
                        'Duplicate date %s in CSV file. '
                        'This file has probably been uploaded before.'
                    ) % book_date
                )


class DocdataPayoutImportForm(CSVImportForm):
    """ Docdata payout import form. """

    dialect = DocdataDialect

    field_mapping = {
        'Period ID': 'period_id',
        'Start date': 'start_date',
        'End date': 'end_date',
        'Total': 'total'
    }

    def _reformat_date(self, date):
        return datetime.datetime.strptime(date, '%d/%m/%y').date()

    def pre_save(self, instance):
        # Fixup date after CSV import
        instance.start_date = self._reformat_date(instance.start_date)
        instance.end_date = self._reformat_date(instance.end_date)

        # If no payout has happened, value should be None
        if instance.total.strip() == '-':
            instance.total = None
        else:
            # Remove ' EUR' suffix from total.
            instance.total = instance.total.replace(' EUR', '')

    def skip_instance(self, instance):
        # Make sure period ID is not already present
        period_id = instance.period_id

        if self.model.objects.filter(period_id=period_id).exists():
            # Already exists, skip
            return True

        return False


class DocdataPaymentImportForm(CSVImportForm):
    """ Docdata payment form. """

    dialect = DocdataDialect

    field_mapping = {
        'Merchant Reference': 'merchant_reference',
        'Triple Deal Reference': 'triple_deal_reference',
        'Type': 'payment_type',
        'Amount Registered': 'amount_registered',
        'Currency Amount Registered': 'currency_amount_registered',
        'Amount Collected': 'amount_collected',
        'Currency Amount Collected': 'currency_amount_collected',
        'TPCD': 'tpcd',
        'Currency TPCD': 'currency_tpcd',
        'TPCI': 'tpci',
        'Currency TPCI': 'currency_tpci',
        'docdata payments Fee': 'docdata_fee',
        'Currency docdata payments Fee': 'currency_docdata_fee',
    }

    def pre_save(self, instance):
        """ Process model instance before saving. """

        if not instance.tpcd:
            # Decimal fields can be None, not empty
            instance.tpcd = None

        if not instance.tpci:
            # Decimal fields can be None, not empty
            instance.tpci = None

    def skip_instance(self, instance):
        if self.model.objects.filter(
            triple_deal_reference=instance.triple_deal_reference,
            merchant_reference=instance.merchant_reference,
            payment_type=instance.payment_type
        ).exists():

            # Already exists, skip
            return True

        return False

