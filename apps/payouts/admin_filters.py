from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

from apps.fund.models import DonationStatuses


class CustomBooleanFilter(SimpleListFilter):
    """
    Base class for custom boolean filters.

    Uses the q_filter Q-object for toggling:
      * 1 / yes -> filter conditions True
      * 0 / no -> filter conditions False
    """

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes')),
            ('0', _('No'))
        )

    def queryset(self, request, queryset):
        assert hasattr(self, 'q_filter')

        if self.value() == '1':
            # Only show payouts with pending donations
            queryset = queryset.filter(self.q_filter)

        elif self.value() == '0':
            # Don't show payouts with pending donations
            queryset = queryset.exclude(self.q_filter)

        # Make sure they're unique - if filtered
        if self.value():
            queryset = queryset.distinct()

        return queryset


class PendingDonationsPayoutFilter(CustomBooleanFilter):
    """ Filter payouts by ones having pending donations. """

    title = _('pending donations')
    parameter_name = 'is_pending'
    q_filter = Q(project__donation__status=DonationStatuses.pending)


class HasIBANPayoutFilter(CustomBooleanFilter):
    """ Filter payouts by whether or not IBAN is set. """

    title = _('has IBAN')
    parameter_name = 'has_iban'

    def queryset(self, request, queryset):

        if self.value() == '1':
            # Only show payouts with pending donations
            queryset = queryset.exclude(receiver_account_iban='').exclude(receiver_account_bic='')

        elif self.value() == '0':
            # Don't show payouts with pending donations
            queryset = queryset.filter(Q(receiver_account_iban='') | Q(receiver_account_bic=''))

        # Make sure they're unique - if filtered
        if self.value():
            queryset = queryset.distinct()

        return queryset
