import re

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


NumericCodeValidator = RegexValidator(re.compile(r'[0-9][0-9][0-9]'),
                                      _("Enter 3 numeric characters."))

Alpha2CodeValidator = RegexValidator(re.compile(r'[A-Z][A-Z]'),
                                     _("Enter 2 capital letters."))

Alpha3CodeValidator = RegexValidator(re.compile(r'[A-Z][A-Z][A-Z]'),
                                     _("Enter 3 capital letters."))
