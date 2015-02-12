import logging
from apps.accounting.models import RemoteDocdataPayment
import re

from bluebottle.payouts.models import ProjectPayout
from bluebottle.utils.utils import StatusDefinition
from django.db.models import Q


logger = logging.getLogger(__name__)


def match_transaction_with_payout(transaction):
    """
    Figure out BankTransactionCategory for given BankTransaction object.

    The category IDs are statically defined in fixtures (initial_data.json).

        1. Campaign payout
        2. Docdata payout
        3. Donation by us
        4. Checking to savings
        5. Savings to checking
        6. Docdata payment

    """
    from apps.accounting.models import RemoteDocdataPayout
    from apps.accounting.models import RemoteDocdataPayment

    full_description = ''.join([getattr(transaction, 'description{0}'.format(i)) for i in range(1, 7)])

    # Matching...
    # Try to match checking to savings
    if transaction.sender_account == 'NL45RABO0132207044' and \
                    transaction.counter_account in ['NL38RABO1513237977', '1513237977']:
        transaction.status = transaction.IntegrityStatus.Valid
        transaction.category_id = 4
        transaction.save()
        return

    # Try to match savings to checking
    if transaction.sender_account == 'NL38RABO1513237977' and \
                    transaction.counter_account in ['NL45RABO0132207044', '0132207044']:
        transaction.status = transaction.IntegrityStatus.Valid
        transaction.category_id = 5
        transaction.save()
        return

    # Figure out possible invoice references
    possible_invoice_refences = [
        getattr(transaction, 'description{0}'.format(i)).split(' ')[0].lower() for i in range(1, 5)
    ]

    # Try to match Project Payout
    # Built query for filtering transactions on invoice reference
    qs_filter = Q()
    for ref in possible_invoice_refences:
        if len(ref) > 0:
            qs_filter |= Q(invoice_reference=ref)

    if qs_filter:
        try:
            project_payout = ProjectPayout.objects.get(qs_filter)
            if project_payout.amount_payable == transaction.amount:
                transaction.status = transaction.IntegrityStatus.Valid
            else:
                transaction.status = transaction.IntegrityStatus.AmountMismatch
                transaction.status_remarks = '{0} != {1}'.format(project_payout.amount_payable, transaction.amount)

            transaction.payout = project_payout
            transaction.category_id = 1
            transaction.save()
            return
        except ProjectPayout.DoesNotExist:
            pass
        except ProjectPayout.MultipleObjectsReturned:
            logger.critical('Multiple project payouts with matching references are found: {0}'.format(', '.join(possible_invoice_refences)))

    # Try to match Docdata Payout
    match = re.search('pop\d+t', full_description)
    if match:
        invoice_reference = match.group()
        try:
            remote_payout = RemoteDocdataPayout.objects.get(payout_reference=invoice_reference)
            if remote_payout.payout_amount == transaction.amount:
                transaction.status = transaction.IntegrityStatus.Valid
            else:
                transaction.status = transaction.IntegrityStatus.AmountMismatch
                transaction.status_remarks = '{0} != {1}'.format(remote_payout.payout_amount, transaction.amount)

            transaction.remote_payout = remote_payout
            transaction.category_id = 2
            transaction.save()
            return
        except RemoteDocdataPayout.DoesNotExist:
            logger.warning('No remote Docdata payout found for reference: {0}'.format(invoice_reference))
        except RemoteDocdataPayout.MultipleObjectsReturned:
            logger.critical('Multiple Docdata payouts with matching triple deal reference are found: {0}'.format(
                invoice_reference))

    # Try to match Docdata Payment
    match = re.search('pid\d+t', full_description)
    if match:
        tdr = match.group()
        try:
            remote_payment = RemoteDocdataPayment.objects.get(triple_deal_reference=tdr)
            if remote_payment.amount_collected == transaction.amount:
                transaction.status = transaction.IntegrityStatus.Valid
            else:
                transaction.status = transaction.IntegrityStatus.AmountMismatch
                transaction.status_remarks = '{0} != {1}'.format(remote_payment.amount_collected, transaction.amount)

            transaction.remote_payment = remote_payment
            transaction.category_id = 6
            transaction.save()
            return
        except RemoteDocdataPayment.DoesNotExist:
            logger.warning('No remote Docdata payment found for triple deal reference: {0}'.format(tdr))
        except RemoteDocdataPayment.MultipleObjectsReturned:
            logger.critical('Multiple Docdata payments with matching triple deal reference are found: {0}'.format(tdr))

    transaction.status = transaction.IntegrityStatus.UnknownTransaction
    transaction.remote_payment = None
    transaction.remote_payout = None
    transaction.payout = None
    transaction.category_id = None
    transaction.save()


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
