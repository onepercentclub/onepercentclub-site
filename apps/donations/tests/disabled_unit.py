from onepercentclub.tests.factory_models.donation_factories import DonationFactory
from onepercentclub.tests.factory_models.fundraiser_factories import FundRaiserFactory
import re

from django.test import TestCase
from django.core import mail

from apps.fund.models import Donation, DonationStatuses
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory

from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory



class DonationMailTests(TestCase):
    def setUp(self):
        self.project_owner = BlueBottleUserFactory.create(email='projectowner@example.com', primary_language='en')
        self.project = OnePercentProjectFactory.create(amount_asked=50000, owner=self.project_owner)
        self.user = BlueBottleUserFactory.create(first_name='Jane')

    def test_mail_owner_on_new_donation(self):
        donation = DonationFactory.create(user=self.user, project=self.project, donation_type=Donation.DonationTypes.one_off)

        # Mailbox should not contain anything.
        self.assertEqual(len(mail.outbox), 0)

        donation.status = DonationStatuses.pending
        donation.save()

        # Owner should have a new email
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]

        self.assertListEqual(message.to, [self.project_owner.email])
        self.assertEqual(message.subject, 'You received a new donation')

        amount_string = 'EUR {0:.2f}'.format(donation.amount / 100.0)
        self.assertTrue(amount_string in message.body)

        for content, content_type in message.alternatives:
            self.assertTrue(amount_string in content)

        self.assertTrue(self.user.first_name in message.body)

    def test_single_mail_on_new_donation(self):
        donation = DonationFactory.create(user=self.user, project=self.project, donation_type=Donation.DonationTypes.one_off)

        # Mailbox should not contain anything.
        self.assertEqual(len(mail.outbox), 0)

        donation.status = DonationStatuses.pending
        donation.save()

        # Save twice!
        donation.save()

        # Save with different status.
        donation.status = DonationStatuses.paid
        donation.save()

        # Owner should have just one email
        self.assertEqual(len(mail.outbox), 1)

    def test_single_mail_on_new_fundraiser_donation(self):

        self.fundraiser_owner = BlueBottleUserFactory.create(email='fundraiserowner@example.com', primary_language='en')
        fundraiser = FundRaiserFactory.create(owner=self.fundraiser_owner, project=self.project)
        donation = DonationFactory.create(user=self.user, project=self.project, donation_type=Donation.DonationTypes.one_off, fundraiser=fundraiser)

        # Mailbox should not contain anything.
        self.assertEqual(len(mail.outbox), 0)

        donation.status = DonationStatuses.pending
        donation.save()

        # Save twice!
        donation.save()

        # Save with different status.
        donation.status = DonationStatuses.paid
        donation.save()

        # Fundraiser owner and project owner should have just one email each
        # careful, fundraiser mail is sent first
        self.assertEqual(len(mail.outbox), 2)

        # Verify that the link points to the fundraiser page
        m = mail.outbox.pop(0)
        match = re.search(r'https?://.*/go/fundraisers/(\d+)', m.body)
        self.assertEqual(int(match.group(1)), fundraiser.id)

        # verify that the mail is indeed directed to the fundraiser owner
        self.assertIn(self.fundraiser_owner.email, m.recipients())