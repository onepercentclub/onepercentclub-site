from apps.donations.models import MonthlyBatch
from django.utils.timezone import now, timedelta


class MonthlyBatchService(object):

    def __init__(self, date=None):
        batches = MonthlyBatch.objects.order_by('-date')
        if batches.count():
            last_batch = batches.all()[0]
        else:
            last_batch = None
        if date:
            self.batch, created = MonthlyBatch.objects.get_or_create(date=date)
            if created:
                self.generate_donations()
        else:
            if last_batch.date > (now() - timedelta(days=10)):
                self.batch = last_batch
            else:
                self.batch = MonthlyBatch.objects.create(date=date)



    def generate_donations(self):
        self.batch
