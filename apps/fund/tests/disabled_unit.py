import json
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory

from django.test import TestCase
from django.test.client import Client
from django.utils import unittest
from django.utils import timezone

from apps.projects.models import Project

from ..models import Order, OrderStatuses, DonationStatuses, RecurringDirectDebitPayment

from rest_framework import status


class RecurringPaymentTest(TestCase):
    def setUp(self):
        self.user = BlueBottleUserFactory.create()

    def test_post_save_disabled(self):
        recurring_payment = RecurringDirectDebitPayment(user=self.user, active=True, name="ABC", city="DEF", account=123)
        recurring_payment.save()

        self.assertTrue(recurring_payment.active)
        self.user.deleted = timezone.now()
        self.user.save()
        recurring_payment = RecurringDirectDebitPayment.objects.get(user=self.user)
        self.assertFalse(recurring_payment.active)

    def test_post_delete_removed(self):
        recurring_payment = RecurringDirectDebitPayment(user=self.user, active=True, name="GHI", city="JKL", account=456)
        recurring_payment.save()

        self.assertTrue(recurring_payment.active)
        self.user.delete()
        recurring_payment = RecurringDirectDebitPayment.objects.filter(user=self.user)
        self.assertEqual(len(recurring_payment), 0)
