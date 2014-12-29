from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import timezone
from bluebottle.bb_payouts.admin import ProjectPayoutAdmin, OrganizationPayoutAdmin
from bluebottle.utils.model_dispatcher import get_project_payout_model, get_organization_payout_model
from django.contrib.admin.sites import NotRegistered

import logging
from bluebottle.utils.admin import export_as_csv_action

logger = logging.getLogger(__name__)


PROJECT_PAYOUT_MODEL = get_project_payout_model()
ORGANIZATION_PAYOUT_MODEL = get_organization_payout_model()


class OnePercentOrganizationPayoutAdmin(OrganizationPayoutAdmin):

    actions = ('export_sepa', )

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
        response.write(ORGANIZATION_PAYOUT_MODEL.create_sepa_xml(objs))
        return response

    export_sepa.short_description = "Export SEPA file."


try:
    admin.site.unregister(ORGANIZATION_PAYOUT_MODEL)
except NotRegistered:
    pass
admin.site.register(ORGANIZATION_PAYOUT_MODEL, OnePercentOrganizationPayoutAdmin)


class OnePercentProjectPayoutAdmin(ProjectPayoutAdmin):

    list_filter = ['status', 'payout_rule', 'project__partner_organization']

    export_fields = ['project', 'status', 'payout_rule', 'amount_raised', 'organization_fee', 'amount_payable',
                     'created', 'submitted']

    actions = ('change_status_to_new', 'change_status_to_progress', 'change_status_to_settled',
               'export_sepa', 'recalculate_amounts', export_as_csv_action(fields=export_fields))

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
        response.write(PROJECT_PAYOUT_MODEL.create_sepa_xml(objs))
        return response

    export_sepa.short_description = "Export SEPA file."

try:
    admin.site.unregister(PROJECT_PAYOUT_MODEL)
except NotRegistered:
    pass
admin.site.register(PROJECT_PAYOUT_MODEL, OnePercentProjectPayoutAdmin)
