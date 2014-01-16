from django.utils.translation import ugettext as _

from djchoices import DjangoChoices, ChoiceItem


class PayoutRules(DjangoChoices):
    """ Which rules to use to calculate fees. """
    old = ChoiceItem('old', label=_("Old 1%/5%"))
    five = ChoiceItem('five', label=_("5%"))
    seven = ChoiceItem('seven', label=_("7%"))
    twelve = ChoiceItem('twelve', label=_("12%"))
    unknown = ChoiceItem('unknown', label=_("Unknown"))
    other = ChoiceItem('other', label=_("Other"))


class PayoutLineStatuses(DjangoChoices):
    """ Status options for payouts. """
    new = ChoiceItem('new', label=_("New"))
    progress = ChoiceItem('progress', label=_("Progress"))
    completed = ChoiceItem('completed', label=_("Completed"))
