from apps.accounting.models import RemoteDocdataPayout
import unicodecsv as csv
import cStringIO as StringIO
import codecs
import itertools

import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.csvimport.utils.common import has_duplicate_items
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


class OldDocdataPaymentImportForm(CSVImportForm):
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


class DocdataPaymentImportForm(forms.Form):
    """
    Form for importing Docdata Payout Detail Report.
    """

    csv_file = forms.FileField(label=_('CSV file'))

    charset = 'utf-8'
    delimiters = '\t'

    field_mapping = {
        'Transaction Id': 'merchant_reference',
        'Payment Id': 'triple_deal_reference',
        # 'Payment Method (Route)': 'payment_method',
        'Description': 'payment_type',
        # 'Direct Paid': 'direct_paid',
        # 'Order Date': 'order_date',
        'Currency Collected': 'currency_amount_collected',
        'Amount Collected': 'amount_collected',
        'Currency Tpci': 'currency_tpci',
        'Tpci': 'tpci',
        'Currency Tdf': 'currency_docdata_fee',
        'Tdf': 'docdata_fee',
    }

    def __init__(self, *args, **kwargs):
        """ Get initialization properties from kwargs. """
        self.model = kwargs.pop('model', None)
        self.payout = None
        super(DocdataPaymentImportForm, self).__init__(*args, **kwargs)

    def pre_save(self, instance):
        """ Process model instance before saving. """
        instance.remote_payout = self.payout

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
        if not instance.amount_collected:
            return True

        return False

    def validate_csv(self, reader):
        """
        Generic validator for CSV contents, run during clean stage.

        Takes reader as parameter and raises ValidationError when
        CSV cannot be validated.

        By default, it does nothing but can be subclassed.
        """
        pass

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']

        # Universal newlines
        # Ugly hack - but works for now
        csv_string = '\n'.join(csv_file.read().splitlines())
        csv_file = StringIO.StringIO(csv_string)

        sniffer = csv.Sniffer()

        # Python's CSV code eats only UTF-8
        csv_file = codecs.EncodedFile(csv_file, self.charset)

        try:
            # Sniff dialect
            dialect = sniffer.sniff(
                csv_string,
                delimiters=self.delimiters
            )

        except csv.Error, e:
            raise forms.ValidationError(
                _('Could not read CSV file: %s' % e.message)
            )

        # Read CSV file
        reader = csv.reader(csv_file, dialect=dialect, encoding=self.charset)

        # Update mapping using header
        t = 1
        while True:
            row = reader.next()
            t += 1
            # Row 10 should have the Payout specification
            if t == 10:
                payout_reference = row[0]
                payout_date = row[1]
                payout_amount = row[3]
                if not payout_reference[:3] == 'pop':
                    error_message = 'Could not find payout details in row 10: {0}'.format(row)
                    raise Exception(error_message)
                self.payout, created = RemoteDocdataPayout.objects.get_or_create(payout_reference=payout_reference)
                self.payout.payout_date = payout_date
                self.payout.payout_amount = payout_amount
                self.payout.save()
            # Row 15 should have the header info for all payments
            if t == 15:
                header = row
                break

        for (key, value) in self.field_mapping.items():
            if isinstance(key, basestring):
                # Key is string, derive number using header
                try:
                    header_index = header.index(key)
                except ValueError:
                    error_message = 'Field %s not found in CSV header.'

                    # Try again with outer spaces removed, and everything
                    # lowercased - but only when no duplicates result
                    header = [f.strip().lower() for f in header]
                    new_key = key.lower()

                    if not has_duplicate_items(header):
                        try:
                            header_index = header.index(new_key)
                        except ValueError:
                            raise Exception(error_message % new_key)
                    else:
                        raise Exception(error_message % key)

                self.field_mapping[header_index] = value

                # Field found, remove from field mapping
                del self.field_mapping[key]

        # Split the iterator such that we can validate
        (reader, validate_fieldcount, validate_csv) = itertools.tee(reader, 3)

        # Validate field count
        validation_row = validate_fieldcount.next()
        if len(self.field_mapping) > len(validation_row):
            raise forms.ValidationError(
                'Less fields in CSV (%d) than specified in field mapping (%d).' % (
                    len(validation_row), len(self.field_mapping)
                )
            )

        # Validate CSV
        if self.validate_csv:
            self.validate_csv(validate_csv)

        self.cleaned_data['csv_reader'] = reader

        return csv_file

    def save(self):
        """ Write results of CSV reader to database according to mapping. """

        new_records = 0
        ignored_records = 0

        for row in self.cleaned_data['csv_reader']:
            init_args = {}

            if len(row) >= len(self.field_mapping):
                for (index, field_name) in self.field_mapping.items():
                    init_args[field_name] = row[index]

                instance = self.model(**init_args)

            # Further processing before saving
            self.pre_save(instance)

            if self.skip_instance(instance):
                # Ignore
                ignored_records += 1

            else:
                # Save
                instance.save()

            new_records += 1

        return (new_records, ignored_records)
