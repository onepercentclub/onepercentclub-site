import uuid

from django.test import TestCase
from django.core import mail

from apps.projects.tests import ProjectTestsMixin
from apps.fund.models import Donation, DonationStatuses, Order


class DonationTestsMixin(object):
    def create_order(self, user, **kwargs):
        # Default values.
        creation_kwargs = {
            'user': user,
            'order_number': unicode(uuid.uuid4())[0:30],  # Unique enough...
        }

        creation_kwargs.update(kwargs)

        return Order.objects.create(**creation_kwargs)

    def create_donation(self, user, project, **kwargs):
        # Default values.
        creation_kwargs = {
            'amount': 100,
            'user': user,
            'project': project,
        }

        creation_kwargs.update(kwargs)

        if 'order' not in creation_kwargs:
            creation_kwargs['order'] = self.create_order(user)

        return Donation.objects.create(**creation_kwargs)


class DonationMailTests(TestCase, ProjectTestsMixin, DonationTestsMixin):
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
        self.assertTrue('EUR {0:.2f}'.format(donation.amount / 100.0) in message.body)
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
