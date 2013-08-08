from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext as _


# Validation references:
# http://www.mobilefish.com/services/elfproef/elfproef.php
# http://www.credit-card.be/BankAccount/ValidationRules.htm#NL_Validation
class DutchBankAccountFieldValidator(RegexValidator):
    main_message = _("Dutch bank account numbers have 1 - 7, 9 or 10 digits.")

    def __init__(self, regex=None, message=None, code=None):
        super(DutchBankAccountFieldValidator, self).__init__(regex='^[0-9]+$', message=self.main_message)

    def __call__(self, value):
        super(DutchBankAccountFieldValidator, self).__call__(value)
        if len(value) != 9 and len(value) != 10 and not 1 <= len(value) <= 7:
            raise ValidationError(self.main_message)

        # Perform the eleven test validation on non-PostBank numbers.
        if len(value) == 9 or len(value) == 10:
            if len(value) == 9:
                value = "0" + value

            eleven_test_sum = sum([int(a)*b for a, b in zip(value, range(1, 11))])
            if eleven_test_sum % 11 != 0:
                raise ValidationError(_("Invalid Dutch bank account number."))


class DutchBankAccountField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 10)
        super(DutchBankAccountField, self).__init__(*args, **kwargs)
        self.validators.append(DutchBankAccountFieldValidator())


# If south is installed, ensure that DutchBankAccountField will be introspected just like a normal CharField
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^apps.fund\.fields\.DutchBankAccountField"])
except ImportError:
    pass
