import decimal

from .choices import PayoutRules


def money_from_cents(amount):
    """
    Convert monetary amount from cents into a Decimal working
    with the MoneyField.
    """

    return decimal.Decimal(amount/100.0)


def round_money(amount):
    """
    Round monetary values specified as Decimal (2 decimals), used for
    displaying results of calculations.
    """

    assert isinstance(amount, decimal.Decimal)

    return amount.quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)


def get_fee_percentage(rule):
    """ Get fee percentag according to specified payment rule. """
    if rule == PayoutRules.five:
        # 5%
        return decimal.Decimal('0.05')

    elif rule == PayoutRules.seven:
        # 7%
        return decimal.Decimal('0.07')

    elif rule == PayoutRules.twelve:
        # 12%
        return decimal.Decimal('0.12')


    # Other
    raise NotImplementedError('Payment rule not implemented yet.')
