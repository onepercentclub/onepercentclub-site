import logging
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
        3. Donation by us (?)
        4. Checking to savings
        5. Savings to checking
        6. Docdata payment

    """

    from apps.accounting.models import RemoteDocdataPayout
    from apps.accounting.models import RemoteDocdataPayment

    full_description = ''.join([getattr(transaction, 'description{0}'.format(i)) for i in range(1, 7)])

    # Try to match checking to savings
    if transaction.sender_account == 'NL45RABO0132207044' and \
                    transaction.counter_account in ['NL38RABO1513237977', '1513237977']:
        transaction.category_id = 4
        transaction.save()
        return

    # Try to match savings to checking
    if transaction.sender_account == 'NL38RABO1513237977' and \
                    transaction.counter_account in ['NL45RABO0132207044', '0132207044']:
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
            transaction.payout = project_payout
            transaction.category_id = 1
            transaction.save()
            return
        except ProjectPayout.DoesNotExist:
            pass
        except ProjectPayout.MultipleObjectsReturned:
            logger.critical('Multiple project payouts with matching references are found: {0}'.format(', '.join(possible_invoice_refences)))

    # # Try to match Docdata Payout
    # if possible_invoice_refences[0][:3] == 'pop':
    #     try:
    #         remote_payout = RemoteDocdataPayout.objects.get(payout_reference=possible_invoice_refences[0])
    #         transaction.remote_payout = remote_payout
    #         transaction.category_id = 2
    #         transaction.save()
    #         return
    #     except RemoteDocdataPayout.DoesNotExist:
    #         logger.warning('No remote Docdata payout found for reference: {0}'.format(possible_invoice_refences[0]))

    # Try to match Docdata Payment
    match = re.search('pid\d+t', full_description)
    if match:
        tdr = match.group()
        try:
            remote_payment = RemoteDocdataPayment.objects.get(triple_deal_reference=tdr)
            transaction.remote_payment = remote_payment
            transaction.category_id = 6
            transaction.save()
            return
        except RemoteDocdataPayment.DoesNotExist:
            logger.warning('No remote Docdata payment found for triple deal reference: {0}'.format(tdr))
        except RemoteDocdataPayment.MultipleObjectsReturned:
            logger.critical('Multiple Docdata payouts with matching triple deal reference are found: {0}'.format(tdr))

    transaction.payout = None
    transaction.category_id = None
    transaction.save()
