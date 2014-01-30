from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

from apps.fund.models import DonationStatuses


class PendingDonationsPayoutFilter(SimpleListFilter):
    """ Filter payouts by ones having pending donations. """

    title = _('pending donations')

    parameter_name = 'is_pending'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes')),
            ('0', _('No'))
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            # Only show payouts with pending donations
            queryset = queryset.filter(
                project__donation__status=DonationStatuses.pending
            )

        elif self.value() == '0':
            # Don't show payouts with pending donations
            queryset = queryset.exclude(
                project__donation__status=DonationStatuses.pending
            )

        # Make sure they're unique - if filtered
        if self.value():
            queryset = queryset.distinct()

        return queryset
