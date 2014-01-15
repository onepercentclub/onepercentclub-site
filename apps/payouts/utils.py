import decimal

from django.conf import settings

from .choices import PayoutRules

VAT_RATE = decimal.Decimal(settings.VAT_RATE)


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

    return amount.quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_HALF_DOWN)


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

def calculate_vat(amount):
    """
    Calculate VAT over exclusive amount according to default percentage.

    >>> calculate_vat(decimal.Decimal('10'))
    Decimal('2.10')
    """

    return round_money(amount * VAT_RATE)

def calculate_vat_inclusive(amount):
    """
    Calculate the inclusive amount for amounts excluding VAT.

    >>> calculate_vat_inclusive(decimal.Decimal('10'))
    Decimal('12.10')
    """

    factor = VAT_RATE + decimal.Decimal('1.00')

    return round_money(amount * factor)

def calculate_vat_exclusive(amount):
    """
    Calculate the exclusive amont for amounts including VAT.

    >>> calculate_vat_exclusive(decimal.Decimal('12.10'))
    Decimal('10.00')
    """

    factor = VAT_RATE + decimal.Decimal('1.00')

    return round_money(amount / factor)
