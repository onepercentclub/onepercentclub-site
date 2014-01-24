import decimal
import datetime

from django.conf import settings
from django.utils import timezone

VAT_RATE = decimal.Decimal(settings.VAT_RATE)


def money_from_cents(amount):
    """
    Convert monetary amount from cents into a Decimal working
    with the MoneyField.

    >>> money_from_cents(1000)
    Decimal('10')
    """

    # Make sure integer work too
    amount = float(amount)

    return decimal.Decimal(str(amount/100))


def round_money(amount):
    """
    Round monetary values specified as Decimal (2 decimals), used for
    displaying results of calculations.
    """

    assert isinstance(amount, decimal.Decimal)

    return amount.quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_HALF_DOWN)


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


def date_timezone_aware(date):
    """
    Create timezone aware datetime equivalent of date, corresponding
    with midnight.
    """
    midnight = datetime.time(0, 0)
    default_zone = timezone.get_default_timezone()

    dt = datetime.datetime.combine(date, midnight)
    dt = timezone.make_aware(dt, default_zone)

    return dt
