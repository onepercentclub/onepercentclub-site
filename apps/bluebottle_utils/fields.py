from django.db import models


class MoneyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_digits', 9)
        kwargs.setdefault('decimal_places', 2)

        super(MoneyField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        # Set 0 as a default amount for money_donated if it hasn't been set yet.
        if getattr(model_instance, self.attname) is None:
            setattr(model_instance, self.attname, 0)

        return super(MoneyField, self).pre_save(model_instance, add)
