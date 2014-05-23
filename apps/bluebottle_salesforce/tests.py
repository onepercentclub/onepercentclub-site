"""
The test cases in bluebottle_salesforce are intended to be used for integration
with Django ORM and Salesforce for Onepercentclub.
"""
import logging
from bluebottle.utils.tests import UserTestsMixin
import requests
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from salesforce import auth
from requests.exceptions import ConnectionError
from django.utils import unittest
from .models import SalesforceOrganization, SalesforceContact, SalesforceDonation, SalesforceProject

logger = logging.getLogger(__name__)

# Define variables
test_email = 'TestEmail@1procentclub.nl'

# Test some settings and skip tests if these settings are not available.
try:
    # Test if a Salesforce database is configured.
    salesforce_db_conf = getattr(settings, 'DATABASES').get('salesforce')
    salesforce_db_conf.get('ENGINE')
    salesforce_db_conf.get('CONSUMER_KEY')
    salesforce_db_conf.get('CONSUMER_SECRET')
    salesforce_db_conf.get('USER')
    salesforce_db_conf.get('PASSWORD')

    # Test if the salesforce server is reachable to see if we're online.
    requests.get(salesforce_db_conf.get('HOST'))

    run_salesforce_tests = True
except (ConnectionError, AttributeError):
    run_salesforce_tests = False


@unittest.skipUnless(run_salesforce_tests, 'Salesforce settings not set or not online')
class OAuthTest(TestCase):
    """
    Test cases verify authentication is working using Django-Salesforce auth with oauth 2.0
    """
    def validate_oauth(self, d):
        """
        Validate input file for oauth 2.0 in secrets.py
        """
        for key in ('access_token', 'id', 'instance_url', 'issued_at', 'signature'):
            if key not in d:
                self.fail("Missing %s key in returned oauth data." % key)
            elif not d[key]:
                self.fail("Empty value for %s key in returned oauth data." % key)

    def test_token_renewal(self):
        """
        Authenticate with Salesforce in real life using oauth 2.0
        """
        auth.authenticate(settings.DATABASES[settings.SALESFORCE_DB_ALIAS])
        self.validate_oauth(auth.oauth_data)
        old_data = auth.oauth_data

        auth.expire_token()
        self.assertEqual(auth.oauth_data, None)

        auth.authenticate(settings.DATABASES[settings.SALESFORCE_DB_ALIAS])
        self.validate_oauth(auth.oauth_data)

        self.assertEqual(old_data['access_token'], auth.oauth_data['access_token'])


@unittest.skipUnless(run_salesforce_tests, 'Salesforce settings not set or not online')
class SalesforceOrganizationTest(TestCase):
    """
    Test cases for Salesforce account object.
    """

    def setUp(self):
        """
        Create our test account record.
        """
        self.test_organization = SalesforceOrganization(name="UserAccount",
                                                        description="Unittest Account",
                                                        email_address=test_email,
                                                        organization_type="Business")
        self.test_organization.save()

    def test_organization_retrieve(self):
        """
        Get the test account record.
        """
        organization = SalesforceOrganization.objects.get(email_address=test_email)
        self.assertEqual(organization.name, 'UserAccount')
        self.assertEqual(organization.description, 'Unittest Account')
        self.assertEqual(organization.organization_type, 'Business')

    def tearDown(self):
        """
        Clean up our test account record.
        """
        self.test_organization.delete()


@unittest.skipUnless(run_salesforce_tests, 'Salesforce settings not set or not online')
class SalesforceContactTest(TestCase):
    """
    Test cases for Salesforce Contact object.
    """

    def setUp(self):
        """
        Create our test Contact record.
        """
        self.test_contact = SalesforceContact(first_name="User",
                                              last_name="Unittest Contact",
                                              email=test_email)
                                              # In the future the below will be used
                                              #Account = "ORG_INDIVIDUAL"
        self.test_contact.save()

    def test_contact_retrieve(self):
        """
        Get the test Contact record.
        """
        contact = SalesforceContact.objects.get(email=test_email)
        self.assertEqual(contact.first_name, 'User')
        self.assertEqual(contact.last_name, 'Unittest Contact')

    def tearDown(self):
        """
        Clean up our test contact record.
        """
        self.test_contact.delete()


@unittest.skipUnless(run_salesforce_tests, 'Salesforce settings not set or not online')
class SalesforceDonationTest(TestCase):
    """
    Test cases for Salesforce Opportunity object.
    """

    def setUp(self):
        """
        Create our test Opportunity record.
        """
        self.test_donation = SalesforceDonation(name="Donation name",
                                                close_date=datetime.strptime("2008-05-05", "%Y-%m-%d"),
                                                stage_name="New")
        self.test_donation.save()

    def test_donation_retrieve(self):
        """
        Get the test Opportunity record.
        """
        donation = SalesforceDonation.objects.get(name="Donation name")
        self.assertEqual(donation.name, 'Donation name')
        self.assertEqual(donation.stage_name, 'New')

    def tearDown(self):
        """
        Clean up our test Opportunity record.
        """
        self.test_donation.delete()


@unittest.skipUnless(run_salesforce_tests, 'Salesforce settings not set or not online')
class SalesforceProjectTest(TestCase):
    """
    Test cases for Salesforce project object.
    """

    def setUp(self):
        """
        Create our test project record.
        """
        self.test_project = SalesforceProject(project_name="ProjectTest",
                                              project_url="http://tweakers.net",
                                              external_id="2468")
        self.test_project.save()

    def test_project_retrieve(self):
        """
        Get the test project record.
        """
        project = SalesforceProject.objects.get(external_id=2468)
        self.assertEqual(project.project_name, 'ProjectTest')
        self.assertEqual(project.project_url, 'http://tweakers.net')

    def tearDown(self):
        """
        Clean up our test project record.
        """
        self.test_project.delete()


@unittest.skipUnless(run_salesforce_tests, 'Salesforce settings not set or not online')
class SyncToSalesforceIntegrationTest(UserTestsMixin, TestCase):
    def smoke_test_sync_script(self):
        #FIXME: We need more objects created here for the test to work.
        # Need to have data for each model that we want to run the smoke test on.
        self.create_user()

        # Run the sync test.
        call_command('sync_to_salesforce', test_run=True)
