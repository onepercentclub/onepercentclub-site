from django.db import models


class MoneyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_digits', 9)
        kwargs.setdefault('decimal_places', 2)

        super(MoneyField, self).__init__(*args, **kwargs)

# Make it work with south introspection
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^apps\.bluebottle_utils\.fields\.MoneyField"])
