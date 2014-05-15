from django.db.models import DecimalField

from south.modelsinspector import add_introspection_rules


class MoneyField(DecimalField):
    """
    Unified reference to fields containing monetary values.

    Currently used in payouts only. Consider putting this in a common
    utils module and using it everywhere - it will make future migrations
    to more advanced monetary fields (i.e. django-money) easier.
    """

    def __init__(self, *args, **kwargs):
        """ Set defaults to 2 decimal places and 12 digits. """
        kwargs['max_digits'] = kwargs.get('max_digits', 12)
        kwargs['decimal_places'] = kwargs.get('decimal_places', 2)

        return super(MoneyField, self).__init__(*args, **kwargs)

add_introspection_rules([], ["^apps\.payouts\.fields\.MoneyField"])
