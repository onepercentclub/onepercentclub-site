import logging
logger = logging.getLogger(__name__)

import decimal

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.text import Truncator

from .models import (
    Payout, PayoutLog, OrganizationPayout, OrganizationPayoutLog,
    BankMutation, BankMutationLine
)
from .choices import PayoutLineStatuses
from .admin_filters import PendingDonationsPayoutFilter, HasIBANPayoutFilter
from .admin_utils import link_to


class PayoutLogBase(admin.TabularInline):
    extra = 0
    max_num = 0
    can_delete = False
    fields = ['date', 'old_status', 'new_status']
    readonly_fields = fields


class PayoutLogInline(PayoutLogBase):
    model = PayoutLog


class OrganizationPayoutLogInline(PayoutLogBase):
    model = OrganizationPayoutLog


class PayoutAdmin(admin.ModelAdmin):
    model = Payout

    inlines = [PayoutLogInline]

    search_fields = [
        'invoice_reference', 'project__title',
        'project__organization__name'
    ]

    date_hierarchy = 'updated'
    can_delete = False

    list_filter = [
        'status', 'payout_rule',
        PendingDonationsPayoutFilter, HasIBANPayoutFilter
    ]

    actions = ['export_sepa', 'recalculate_amounts']

    list_display = [
        'payout', 'status', 'admin_project', 'amount_payable',
        'admin_amount_raised', 'admin_amount_pending', 'is_pending',
        'payout_rule', 'updated', 'admin_has_iban'
    ]

    list_display_links = [
        'payout',
    ]


    readonly_fields = [
        'admin_project', 'admin_organization', 'created', 'updated',
        'admin_amount_safe', 'admin_amount_pending', 'admin_amount_failed'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'admin_project', 'admin_organization',
                'status', 'invoice_reference'
            )
        }),
        (_('Dates'), {
            'fields': (
                'created', 'updated', 'completed',
            )
        }),
        (_('Realtime amounts'), {
            'fields': (
                'admin_amount_safe', 'admin_amount_pending', 'admin_amount_failed'
            )
        }),
        (_('Payout amounts'), {
            'fields': ('amount_raised', 'organization_fee', 'amount_payable', 'payout_rule')
        }),
        (_('Payment details'), {
            'fields': (
                'receiver_account_country', 'receiver_account_number', 'receiver_account_iban', 'receiver_account_bic',
                'description_line1', 'description_line2', 'description_line3', 'description_line4'
            )
        })
    )

    def is_pending(self, obj):
        """ Whether or not there is no amount pending. """
        if obj.get_amount_pending() == decimal.Decimal('0.00'):
            return False

        return True
    is_pending.boolean = True
    is_pending.short_description = _('pending')

    # Link to all donations for project
    admin_amount_raised = link_to(
        'amount_raised', 'admin:fund_donation_changelist',
        query=lambda obj: {
            'project': obj.project.id,
            'status__exact': 'all'
        },
        short_description=_('amount raised')
    )

    # Link to pending donations for project
    admin_amount_pending = link_to(
        lambda obj: obj.get_amount_pending(), 'admin:fund_donation_changelist',
        query=lambda obj: {
            'project': obj.project.id,
            'status__exact': 'pending'
        },
        short_description=_('amount pending')
    )

    # Link to paid donations for project
    admin_amount_safe = link_to(
        lambda obj: obj.get_amount_safe(), 'admin:fund_donation_changelist',
        query=lambda obj: {
            'project': obj.project.id,
            'status__exact': 'paid'
        },
        short_description=_('amount safe')
    )

    # Link to failed donations for project
    admin_amount_failed = link_to(
        lambda obj: obj.get_amount_failed(), 'admin:fund_donation_changelist',
        query=lambda obj: {
            'project': obj.project.id,
            'status__exact': 'failed'
        },
        short_description=_('amount failed')
    )

    # Link to project
    def admin_project(self, obj):
        """ Link to project in front end. """
        project = obj.project

        return u'<a href="/#!/projects/{0}">{1}</a>'.format(
            project.slug, Truncator(unicode(project)).chars(35)
        )
    admin_project.allow_tags = True
    admin_project.short_description = _('project')

    # Link to organization
    admin_organization = link_to(
        lambda obj: obj.project.organization,
        'admin:organizations_organization_change',
        view_args=lambda obj: (obj.project.projectplan.organization.id, ),
        short_description=_('organization')
    )

    def admin_has_iban(self, obj):
        if obj.receiver_account_iban:
            return True

        return False
    admin_has_iban.short_description = _('has IBAN')
    admin_has_iban.boolean = True

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
    inlines = [OrganizationPayoutLogInline]

    can_delete = False

    search_fields = ['invoice_reference']

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

    fieldsets = (
        (None, {
            'fields': (
                'status', 'invoice_reference'
            )
        }),
        (_('Dates'), {
            'fields': (
                'start_date', 'end_date', 'planned', 'completed'
            )
        }),
        (_('Organization fee'), {
            'fields': (
                'organization_fee_excl', 'organization_fee_vat', 'organization_fee_incl'
            )
        }),
        (_('PSP fee'), {
            'fields': (
                'psp_fee_excl', 'psp_fee_vat', 'psp_fee_incl'
            )
        }),
        (_('Other costs'), {
            'fields': (
                'other_costs_excl', 'other_costs_vat', 'other_costs_incl'
            )
        }),
        (_('Amount payable'), {
            'fields': (
                'payable_amount_excl', 'payable_amount_vat', 'payable_amount_incl'
            )
        })
    )

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

# admin.site.register(BankMutation, BankMutationAdmin)


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

# admin.site.register(BankMutationLine, BankMutationLineAdmin)

