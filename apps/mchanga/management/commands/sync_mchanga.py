from django.core.management.base import BaseCommand
from apps.mchanga.adapters import MchangaService


class Command(BaseCommand):
    help = 'Synchronize M-Changa payments.'

    def handle(self, *args, **options):
        service = MchangaService()
        service.sync_payments()
        service.sync_fundraisers()
