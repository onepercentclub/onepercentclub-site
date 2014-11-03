from bluebottle.bb_payouts.admin import ProjectPayoutAdmin
from bluebottle.utils.model_dispatcher import get_project_payout_model
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered

PROJECT_PAYOUT_MODEL = get_project_payout_model()


class OnePercentProjectPayoutAdmin(ProjectPayoutAdmin):

    list_filter = ['status', 'payout_rule', 'project__partner_organization']

try:
    admin.site.unregister(PROJECT_PAYOUT_MODEL)
except NotRegistered:
    pass
admin.site.register(PROJECT_PAYOUT_MODEL, OnePercentProjectPayoutAdmin)
