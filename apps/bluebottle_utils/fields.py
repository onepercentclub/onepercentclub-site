from decimal import Decimal
from django.db import models


class MoneyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_digits', 9)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('default', Decimal('0.00'))
        super(MoneyField, self).__init__(*args, **kwargs)


# If south is installed, ensure that MoneyField will be introspected just like a normal DecimalField
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], ["^apps\.bluebottle_utils\.fields\.MoneyField",])
