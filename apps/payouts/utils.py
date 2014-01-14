from decimal import Decimal


def money_from_cents(amount):
    """
    Convert monetary amount from cents into a Decimal working
    with the MoneyField.
    """

    return Decimal(amount/100.0)
