import os

from django.test import TestCase

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from .models import BankTransaction, DocdataPayout, DocdataPayment


class AdminTestMixin(object):
    """ Mixin for testing Admin modules. """

    def setUp(self):
        super(AdminTestMixin, self).setUp()

        user_model = get_user_model()

        # Setup admin user
        self.adminuser = user_model.objects.create_user(
            'admin@test.com', 'pass'
        )
        self.adminuser.is_staff = True
        self.adminuser.is_superuser = True
        self.adminuser.save()

        # Login admin user
        self.client.login(username='admin@test.com', password='pass')


class ImportTestMixin(object):
    """ Mixin for testing import modules. """

    def setUp(self):
        super(ImportTestMixin, self).setUp()

        self.import_url = reverse(self.import_view)

    def test_form(self):
        """ Test import form and URL. """
        # Attempt a mere get
        response = self.client.get(self.import_url)
        self.assertContains(response, 'import')
        self.assertContains(response, 'csv_file')

    def import_csv(self):
        """
        Import CSV file. Common helper method.
        """

        csv_filename = os.path.join(
            os.path.dirname(__file__), 'test_assets', self.csv_file
        )

        with open(csv_filename, 'rb') as csv_file:
            response = self.client.post(
                self.import_url, {
                    'csv_file': csv_file
                },
                follow=True
            )

        return response

    def test_import(self):
        """
        Test import of CSV file.
        """

        response = self.import_csv()

        # Assert records have been imported
        self.assertContains(response, 'records have been imported')

        self.assertTrue(self.model.objects.exists())

    def test_duplicate_import(self):
        """ Importing twice should not import any extra records. """

        self.import_csv()
        object_count = self.model.objects.count()

        self.import_csv()

        self.assertEquals(
            object_count, self.model.objects.count()
        )


class BankImportTest(AdminTestMixin, ImportTestMixin, TestCase):
    """ Test import of bank statements. """

    model = BankTransaction
    import_view = 'admin:accounting_banktransaction_import'
    csv_file = 'bank.csv'

    def test_duplicate_date_exception(self):
        """ Make sure uploading twice yields a form error. """

        self.import_csv()
        response = self.import_csv()

        form_errors = response.context['adminform'].form.errors

        self.assertEquals(len(form_errors.get('csv_file', [])), 1)


class DocdataPayoutTest(AdminTestMixin, ImportTestMixin, TestCase):
    """ Test import of Docdata payments. """

    model = DocdataPayout
    import_view = 'admin:accounting_docdatapayout_import'
    csv_file = 'docdata_payout.csv'


class DocdataPaymentTest(AdminTestMixin, ImportTestMixin, TestCase):
    """ Test import of Docdata payments. """

    model = DocdataPayment
    import_view = 'admin:accounting_docdatapayment_import'
    csv_file = 'docdata_payments.csv'
