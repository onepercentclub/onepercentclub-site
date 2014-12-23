from bluebottle.payouts.models import ProjectPayout
from bluebottle.utils.utils import StatusDefinition


def match_transaction_with_payout(transaction):

    line = transaction.description1.split(' ')

    if len(line) > 0:
        invoice_reference = line[0]
        try:
            transaction.payout = ProjectPayout.objects.get(invoice_reference=invoice_reference)
            transaction.category_id = 1
            transaction.save()
        except ProjectPayout.DoesNotExist:
            pass


def match_transaction_with_payout_on_creation(sender, instance, created, **kwargs):

    transaction = instance
    if not transaction.payout:

        match_transaction_with_payout(transaction)


def change_payout_status_with_matched_transaction(sender, instance, created, **kwargs):

    transaction = instance

    if transaction.payout:
        payout = transaction.payout
        payout.status = StatusDefinition.SETTLED
        payout.completed = transaction.book_date
        payout.save()
