import re

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.formats import number_format
from django.template import Library


register = Library()


@register.filter(is_safe=True)
def numberformat(value, use_l10n=True):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    if not value:
        value = 0

    if settings.USE_L10N and use_l10n:
        return number_format(value, force_grouping=True)
    orig = force_text(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return numberformat(new, use_l10n)
