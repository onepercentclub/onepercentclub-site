from decimal import Decimal

from .choices import PayoutRules


def money_from_cents(amount):
    """
    Convert monetary amount from cents into a Decimal working
    with the MoneyField.
    """

    return Decimal(amount/100.0)


def get_fee_percentage(rule):
    """ Get fee percentag according to specified payment rule. """
    if rule == PayoutRules.five:
        # 5%
        return Decimal('0.05')

    elif rule == PayoutRules.seven:
        # 7%
        return Decimal('0.07')

    elif rule == PayoutRules.twelve:
        # 12%
        return Decimal('0.12')


    # Other
    raise NotImplementedError('Payment rule not implemented yet.')
