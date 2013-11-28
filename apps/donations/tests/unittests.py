import re

from django.test import TestCase
from django.core import mail

from apps.projects.tests import ProjectTestsMixin
from apps.fund.models import Donation, DonationStatuses
from apps.fundraisers.tests.helpers import FundRaiserTestsMixin

from .helpers import DonationTestsMixin


class DonationMailTests(TestCase, ProjectTestsMixin, DonationTestsMixin, FundRaiserTestsMixin):
    def setUp(self):
        self.project_owner = self.create_user(email='projectowner@example.com', primary_language='en')
        self.project = self.create_project(money_asked=50000, owner=self.project_owner)
        self.user = self.create_user(first_name='Jane')

    def test_mail_owner_on_new_donation(self):
        donation = self.create_donation(self.user, self.project, donation_type=Donation.DonationTypes.one_off)

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
        donation = self.create_donation(self.user, self.project, donation_type=Donation.DonationTypes.one_off)

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
        self.fundraiser_owner = self.create_user(email='fundraiserowner@example.com', primary_language='en')
        fundraiser = self.create_fundraiser(self.fundraiser_owner, self.project)
        donation = self.create_donation(self.user, self.project, donation_type=Donation.DonationTypes.one_off, fundraiser=fundraiser)

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