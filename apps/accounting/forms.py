import logging
from decimal import Decimal, InvalidOperation
import unicodecsv as csv
import cStringIO as StringIO
import codecs
import itertools
import datetime

from django.db.models import Sum
from django import forms
from django.utils.translation import ugettext_lazy as _

from bluebottle.payments_docdata.models import DocdataPayment, DocdataDirectdebitPayment

from apps.csvimport.utils.common import has_duplicate_items
from apps.csvimport.forms import CSVImportForm
from apps.accounting.fields import MultiFileField
from apps.accounting.models import RemoteDocdataPayout, RemoteDocdataPayment

from .dialects import DocdataDialect


logger = logging.getLogger(__name__)


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


class DocdataPaymentImportForm(forms.Form):
    """
    Form for importing Docdata Payout Detail Report.
    """

    csv_file = MultiFileField(label=_('Payout Details Report'),
                               help_text=_('Docdata Back-office > Reports > Download Reports > Payout Details Report + csv '),
                               maximum_file_size=1024*1024)


    charset = 'utf-8'
    dialect = DocdataDialect
    delimiters = '\t'
    csv_reader = []
    payouts = []

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
        self.payouts = []
        self.csv_reader = []
        super(DocdataPaymentImportForm, self).__init__(*args, **kwargs)

    def pre_save(self, instance, payout):
        """ Process model instance before saving. """
        instance.remote_payout = payout

        if not instance.tpcd:
            # Decimal fields can be None, not empty
            instance.tpcd = None

        if not instance.tpci:
            # Decimal fields can be None, not empty
            instance.tpci = None

    def skip_instance(self, instance):
        if RemoteDocdataPayment.objects.filter(
            triple_deal_reference=instance.triple_deal_reference,
            payment_type=instance.payment_type
        ).exists():

            # Already exists, skip
            logger.warning('Record already exists: {0}'.format(instance.triple_deal_reference))
            return True
        if not instance.amount_collected:
            logger.warning('Record has no amount: {0}'.format(instance.triple_deal_reference))
            return True
        try:
            Decimal(instance.amount_collected)
        except InvalidOperation:
            logger.warning('Record has an invalid amount ({0}): {1}'.format(
                instance.amount_collected, instance.triple_deal_reference))
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


    def parse_csv_file(self, csv_file):
        # Universal newlines
        # Ugly hack - but works for now
        csv_string = '\n'.join(csv_file.read().splitlines())
        csv_file = StringIO.StringIO(csv_string)

        sniffer = csv.Sniffer()

        # Python's CSV code eats only UTF-8
        csv_file = codecs.EncodedFile(csv_file, self.charset)

        dialect = self.dialect

        # Read CSV file
        reader = csv.reader(csv_file, dialect=dialect, encoding=self.charset)

        # Update mapping using header
        t = 1
        while True:
            row = reader.next()
            t += 1
            # Row 3 (cell 2) holds the dates for the payments in this payout
            if t == 4:
                interval = row[1].split(' to ')
                payout_start = interval[0].strip(' 00:00')
                payout_end = interval[1].strip(' 00:00')
            # Row 10 should have the Payout specification
            if t == 10:
                payout_reference = row[0]
                payout_date = row[1]
                payout_amount = row[3]
                if not payout_reference[:3] == 'pop':
                    error_message = 'Could not find payout details in row 10: {0}'.format(row)
                    raise Exception(error_message)
                payout, created = RemoteDocdataPayout.objects.get_or_create(payout_reference=payout_reference)
                payout.payout_date = payout_date
                payout.payout_amount = payout_amount

                payout.start_date = payout_start
                payout.end_date = payout_end
                payout.save()
                self.payouts.append(payout)
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

        self.csv_reader.append(reader)
        return csv_file

    def clean_csv_file(self):
        files = self.cleaned_data['csv_file']
        self.cleaned_data['csv_file'] = []
        for csv_file in files:
            self.cleaned_data['csv_file'].append(self.parse_csv_file(csv_file))
        return self.cleaned_data['csv_file']

    def save(self):
        """ Write results of CSV reader to database according to mapping. """

        new_records = 0
        ignored_records = 0

        for csv_reader in self.csv_reader:
            payout = self.payouts.pop(0)
            for row in csv_reader:
                init_args = {}

                if len(row) >= len(self.field_mapping):
                    for (index, field_name) in self.field_mapping.items():
                        init_args[field_name] = row[index]

                    instance = RemoteDocdataPayment(**init_args)

                # Further processing before saving
                self.pre_save(instance, payout)

                if self.skip_instance(instance):
                    # Ignore
                    ignored_records += 1

                else:
                    # NOTE: Could be moved to pre_save, but skipped records are also processed in that case.
                    # Update status and remarks
                    if not instance.merchant_reference:
                        instance.status = RemoteDocdataPayment.IntegrityStatus.MissingBackofficeRecord
                        instance.status_remarks = 'Merchant reference missing'
                    else:
                        local_payment = None
                        try:
                            local_payment = DocdataPayment.objects.get(payment_cluster_id=instance.merchant_reference)
                        except DocdataPayment.DoesNotExist:
                            try:
                                local_payment = DocdataDirectdebitPayment.objects.get(merchant_order_id=instance.merchant_reference)
                            except DocdataDirectdebitPayment.DoesNotExist:
                                pass

                        if local_payment:
                            instance.local_payment = local_payment
                            amount_collected = Decimal(instance.amount_collected)

                            if instance.payment_type in ['chargedback', 'refund'] and \
                                                    amount_collected * -1 == local_payment.order_payment.amount:
                                instance.status = RemoteDocdataPayment.IntegrityStatus.Valid
                            elif amount_collected == local_payment.order_payment.amount:
                                instance.status = RemoteDocdataPayment.IntegrityStatus.Valid
                            else:
                                # Case missing: multiple payments (even in different payouts). Mark as invalid now, and
                                # check afterwards.
                                instance.status = RemoteDocdataPayment.IntegrityStatus.AmountMismatch
                                instance.status_remarks = '{0} != {1}'.format(amount_collected,
                                                                              local_payment.order_payment.amount)
                        else:
                            instance.status = RemoteDocdataPayment.IntegrityStatus.MissingBackofficeRecord

                    # Save
                    instance.save()

                new_records += 1

            # Missing case: multiple payments can be figured out after processing all entries. This will be done over
            # all existing records to even cover payouts over several weeks.
            queryset = RemoteDocdataPayment.objects.filter(
                status=RemoteDocdataPayment.IntegrityStatus.AmountMismatch
            ).annotate(
               rdp_amount_collected_sum=Sum('local_payment__remotedocdatapayment__amount_collected')
            )

            pks = []
            for pk, rdp_sum, local_amount in queryset.values_list('pk', 'rdp_amount_collected_sum', 'local_payment__order_payment__amount'):
                if rdp_sum == local_amount:
                    pks.append(pk)

            if pks:
                RemoteDocdataPayment.objects.filter(pk__in=pks).update(
                    status = RemoteDocdataPayment.IntegrityStatus.Valid,
                    status_remarks = 'Multiple payments',
                )

        return (new_records, ignored_records)
