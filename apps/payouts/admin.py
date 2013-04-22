import logging
from apps.payouts.models import create_sepa_xml, create_upcoming_payouts
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import timezone

logger = logging.getLogger(__name__)

from django.contrib import admin

from .models import Payout


class PayoutAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        create_upcoming_payouts()
        print "Doing great here..."
        super(PayoutAdmin, self).__init__(model, admin_site)

    model = Payout
    can_delete = False

    actions = ['export_sepa']

    list_display = ['payout', 'ok', 'donation_overview', 'project', 'local_amount', 'local_amount_safe',
                    'receiver_account_number', 'invoice_reference', 'status']

    readonly_fields = ['donation_overview', 'project', 'local_amount', 'local_amount_safe', 'status', 'ok']
    fields = readonly_fields + ['receiver_account_number', 'receiver_account_iban', 'receiver_account_bic',
                                'receiver_account_country', 'invoice_reference', 'description_line1',
                                'description_line2', 'description_line3', 'description_line4']

    def donation_overview(self, obj):
        return "<a href='/admin/fund/donation/?project=%s'>Donations</a>" % str(obj.project.id)

    donation_overview.allow_tags = True

    def ok(self, obj):
        if obj.is_valid:
            return "OK"
        return "-"

    donation_overview.allow_tags = True

    def payout(self, obj):
        return "View/Edit"

    def has_add_permission(self, request):
        return False

    def export_sepa(self, request, queryset):
        """
        Dowload a sepa file with selected ProjectPayments
        """
        objs = queryset.all()
        if not request.user.is_staff:
            raise PermissionDenied
        response = HttpResponse(mimetype='text/xml')
        date = timezone.datetime.strftime(timezone.now(), '%Y%m%d%H%I%S')
        response['Content-Disposition'] = 'attachment; filename=payments_sepa%s.xml' % date
        response.write(create_sepa_xml(objs))
        return response

    export_sepa.short_description = "Export SEPA file."

admin.site.register(Payout, PayoutAdmin)

