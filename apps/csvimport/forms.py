import unicodecsv as csv
import cStringIO as StringIO
import codecs
import itertools

from django import forms
from django.utils.translation import ugettext_lazy as _

from .utils.common import has_duplicate_items


class CSVImportForm(forms.Form):
    """
    Form used for importing and uploading of CSV-file.

    This form uses a dictionary `import_field_mapping` to be defined in
    the admin class, specifying how CSV fields should be mapped to model
    fields. CSV fields in `import_field_mapping` can be identified either by
    column number or by the column header (if present).

    Example::

        class MyImportingAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
            import_field_mapping = {
                0: 'sender_account',
                1: 'currency',
                2: 'interest_date',
                3: 'credit_debet',
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
    """

    csv_file = forms.FileField(label=_('CSV file'))

    charset = 'utf-8'
    delimiters = ';\t,'

    # Import dialect; overrides dialect detection when specified
    dialect = None

    def __init__(self, *args, **kwargs):
        """ Get initialization properties from kwargs. """

        assert hasattr(self, 'field_mapping'), \
            'No field mapping defined.'
        assert isinstance(self.field_mapping, dict), \
            'Field mapping is not a dictionary'

        self.model = kwargs.pop('model', None)

        super(CSVImportForm, self).__init__(*args, **kwargs)

    def pre_save(self, instance):
        """
        This method is called with model instance before saving.

        By default, it does nothing but can be subclassed.
        """
        pass

    def skip_instance(self, instance):
        """
        Wheter or not to skip an instance on import.
        Called after pre_save().

        Returns True or False.

        By default, it does not skip any entries.
        """
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

        # TODO: Use chardet
        # Ref: https://github.com/dokterbob/django-newsletter/blob/master/newsletter/admin_forms.py#L86
        sniffer = csv.Sniffer()

        # Python's CSV code eats only UTF-8
        csv_file = codecs.EncodedFile(csv_file, self.charset)

        try:
            if self.dialect:
                # Override dialect, don't autodetect
                dialect = self.dialect
            else:
                # Sniff dialect
                dialect = sniffer.sniff(
                    csv_string,
                    delimiters=self.delimiters
                )

            # Sniff for a header
            has_header = sniffer.has_header(
                csv_string
            )

        except csv.Error, e:
            raise forms.ValidationError(
                _('Could not read CSV file: %s' % e.message)
            )

        # Read CSV file
        reader = csv.reader(csv_file,
            dialect=dialect, encoding=self.charset
        )

        if has_header:
            # Update mapping using header
            header = reader.next()

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
