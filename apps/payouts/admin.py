import logging
from apps.payouts.models import create_sepa_xml
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import timezone
from .models import BankMutation, BankMutationLine

logger = logging.getLogger(__name__)

from django.contrib import admin

from .models import Payout


class PayoutAdmin(admin.ModelAdmin):

    model = Payout
    can_delete = False

    list_filter = ['status']

    actions = ['export_sepa']

    list_display = ['payout', 'ok', 'donation_overview', 'project', 'local_amount', 'local_amount_safe',
                    'receiver_account_number', 'invoice_reference', 'status']

    readonly_fields = ['donation_overview', 'project', 'local_amount', 'local_amount_safe']
    fields = readonly_fields + ['status', 'receiver_account_number', 'receiver_account_iban', 'receiver_account_bic',
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


class BankMutationAdmin(admin.ModelAdmin):
    model = BankMutation
    save_on_top = True
    actions_on_top = True

    def credit_lines(self, obj):
        return "<a href='/admin/payouts/bankmutationline/?bank_mutation=%s&dc=C'>Credit mutations</a>" % str(obj.id)

    credit_lines.allow_tags = True

    def debit_lines(self, obj):
        return "<a href='/admin/payouts/bankmutationline/?bank_mutation=%s&dc=D'>Debit mutations</a>" % str(obj.id)

    debit_lines.allow_tags = True

    readonly_fields = ['debit_lines', 'credit_lines']
    fields = readonly_fields + ['mut_file', ]

admin.site.register(BankMutation, BankMutationAdmin)


class BankMutationLineAdmin(admin.ModelAdmin):
    model = BankMutationLine
    list_filter = ['dc']
    can_delete = False
    extra = 0

    list_display = ['start_date', 'matched', 'dc', 'transaction_type', 'amount', 'invoice_reference', 'account_number', 'account_name']

    def has_add_permission(self, request):
        return False

    def matched(self, obj):
        if obj.payout:
            return "Yes"
        return "-"

    matched.allow_tags = True

    readonly_fields = ['bank_mutation', 'amount', 'dc', 'transaction_type', 'account_number', 'account_name',
                       'start_date', 'matched', 'issuer_account_number', 'currency', 'invoice_reference',
                       'description_line1', 'description_line2', 'description_line3', 'description_line4']
    #fields = readonly_fields

admin.site.register(BankMutationLine, BankMutationLineAdmin)

