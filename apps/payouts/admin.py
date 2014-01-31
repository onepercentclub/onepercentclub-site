import logging
logger = logging.getLogger(__name__)

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext as _

from .models import Payout, OrganizationPayout, BankMutation, BankMutationLine
from .choices import PayoutLineStatuses


class PayoutAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'

    model = Payout
    can_delete = False

    list_filter = ['status', 'payout_rule']

    actions = ['export_sepa', 'recalculate_amounts']

    list_display = [
        'payout', 'ok', 'donation_overview', 'project',
        'amount_raised', 'organization_fee', 'amount_payable', 'safe_amount_payable',
        'receiver_account_number', 'invoice_reference', 'status', 'completed'
    ]

    readonly_fields = [
        'donation_overview', 'project_link', 'organization',
        'safe_amount_payable'
    ]

    fields = readonly_fields + [
        'amount_raised', 'organization_fee', 'amount_payable', 'payout_rule',
        'status', 'completed', 'receiver_account_number', 'receiver_account_iban', 'receiver_account_bic',
        'receiver_account_country', 'invoice_reference', 'description_line1',
        'description_line2', 'description_line3', 'description_line4'
    ]


    def organization(self, obj):
        object = obj.project.projectplan.organization
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.name)

    organization.allow_tags = True


    def donation_overview(self, obj):
        return "<a href='/admin/fund/donation/?project=%s'>Donations</a>" % str(obj.project.id)

    donation_overview.allow_tags = True

    def project_link(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    project_link.allow_tags = True
    project_link.short_description = _('project')

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
        response.write(Payout.create_sepa_xml(objs))
        return response

    export_sepa.short_description = "Export SEPA file."

    def recalculate_amounts(self, request, queryset):
        # Only recalculate for 'new' payouts
        filter_args = {'status': PayoutLineStatuses.new}
        qs_new = queryset.all().filter(**filter_args)

        for payout in qs_new:
            payout.calculate_amounts()

        message = (
            "Fees for %(new_payouts)d new payouts were recalculated. "
            "%(skipped_payouts)d progressing or closed payouts have been skipped."
        ) % {
            'new_payouts': qs_new.count(),
            'skipped_payouts': queryset.exclude(**filter_args).count()
        }

        self.message_user(request, message)

    recalculate_amounts.short_description = _("Recalculate amounts for new payouts.")

admin.site.register(Payout, PayoutAdmin)


class OrganizationPayoutAdmin(admin.ModelAdmin):
    can_delete = False

    date_hierarchy = 'start_date'

    list_filter = ['status', ]

    list_display = [
        'invoice_reference', 'start_date', 'end_date',
        'organization_fee_incl', 'psp_fee_incl',
        'other_costs_incl', 'payable_amount_incl'
    ]

    readonly_fields = [
        'invoice_reference', 'organization_fee_excl', 'organization_fee_vat', 'organization_fee_incl',
        'psp_fee_excl', 'psp_fee_vat', 'psp_fee_incl',
        'payable_amount_excl', 'payable_amount_vat', 'payable_amount_incl',
        'other_costs_vat'
    ]

    actions = ['recalculate_amounts']

    def recalculate_amounts(self, request, queryset):
        # Only recalculate for 'new' payouts
        filter_args = {'status': PayoutLineStatuses.new}
        qs_new = queryset.all().filter(**filter_args)

        for payout in qs_new:
            payout.calculate_amounts()

        message = (
            "Amounts for %(new_payouts)d new payouts were recalculated. "
            "%(skipped_payouts)d progressing or closed payouts have been skipped."
        ) % {
            'new_payouts': qs_new.count(),
            'skipped_payouts': queryset.exclude(**filter_args).count()
        }

        self.message_user(request, message)

    recalculate_amounts.short_description = _("Recalculate amounts for new payouts.")

admin.site.register(OrganizationPayout, OrganizationPayoutAdmin)


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

    list_display = [
        'start_date', 'matched', 'dc', 'transaction_type', 'amount', 'invoice_reference', 'account_number', 'account_name'
    ]

    def has_add_permission(self, request):
        return False

    def matched(self, obj):
        if obj.payout:
            return "Yes"
        return "-"

    matched.allow_tags = True

    readonly_fields = [
        'bank_mutation', 'amount', 'dc', 'transaction_type', 'account_number', 'account_name',
       'start_date', 'matched', 'issuer_account_number', 'currency', 'invoice_reference',
       'description_line1', 'description_line2', 'description_line3', 'description_line4'
    ]
    #fields = readonly_fields

admin.site.register(BankMutationLine, BankMutationLineAdmin)

