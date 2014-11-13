from bluebottle.bb_payouts.admin import ProjectPayoutAdmin
from bluebottle.utils.admin import export_as_csv_action
from bluebottle.utils.model_dispatcher import get_project_payout_model
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered

PROJECT_PAYOUT_MODEL = get_project_payout_model()


class OnePercentProjectPayoutAdmin(ProjectPayoutAdmin):

    list_filter = ['status', 'payout_rule', 'project__partner_organization']

    export_fields = ['project', 'status', 'payout_rule', 'amount_raised', 'organization_fee', 'amount_payable',
                     'created', 'submitted']

    actions = ('export_sepa', 'recalculate_amounts', export_as_csv_action(fields=export_fields))

try:
    admin.site.unregister(PROJECT_PAYOUT_MODEL)
except NotRegistered:
    pass
admin.site.register(PROJECT_PAYOUT_MODEL, OnePercentProjectPayoutAdmin)
