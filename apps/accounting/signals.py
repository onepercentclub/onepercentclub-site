from bluebottle.payouts.models import ProjectPayout
from bluebottle.utils.utils import StatusDefinition


def match_transaction_with_payout(transaction):

    from apps.accounting.models import RemoteDocdataPayout

    # Try to match Project Payout
    line = transaction.description1.split(' ')
    if len(line) > 0:
        invoice_reference = line[0].lower()
        try:
            transaction.payout = ProjectPayout.objects.get(invoice_reference=invoice_reference)
            transaction.category_id = 1
            transaction.save()
        except ProjectPayout.DoesNotExist:
            pass

    line = transaction.description3.split(' ')[0]
    if len(line) > 0:
        invoice_reference = line.lower()
        try:
            transaction.payout = ProjectPayout.objects.get(invoice_reference=invoice_reference)
            transaction.category_id = 1
            transaction.save()
        except ProjectPayout.DoesNotExist:
            pass

    line = transaction.description4.split(' ')[0]
    if len(line) > 0:
        invoice_reference = line.lower()
        try:
            transaction.payout = ProjectPayout.objects.get(invoice_reference=invoice_reference)
            transaction.category_id = 1
            transaction.save()
        except ProjectPayout.DoesNotExist:
            pass

    # Try to match Docdata Payout
    line = transaction.description1.split(' ')
    invoice_reference = line[0].lower()
    print invoice_reference[:3]
    if invoice_reference[:3] == 'pop':
        try:
            transaction.remote_payout = RemoteDocdataPayout.objects.get(payout_reference=invoice_reference)
            transaction.category_id = 2
            transaction.save()
        except RemoteDocdataPayout.DoesNotExist:
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
