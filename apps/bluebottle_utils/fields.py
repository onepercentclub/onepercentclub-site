from django.db import models


class MoneyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_digits', 9)
        kwargs.setdefault('decimal_places', 2)

        super(MoneyField, self).__init__(*args, **kwargs)
