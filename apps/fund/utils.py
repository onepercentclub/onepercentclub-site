from apps.cowry import factory


def get_order_payment_methods(order):
    # Cowry payments use minor currency units so we need to convert the Euros to cents.
    amount = int(order.amount * 100)
    return factory.get_payment_methods(amount=amount, currency='EUR', country='NL', recurring=order.recurring)

