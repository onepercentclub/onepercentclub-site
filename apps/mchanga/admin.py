from apps.mchanga.models import MpesaPayment
from bluebottle.utils.admin import export_as_csv_action
from django.contrib import admin


class MpesaAdmin(admin.ModelAdmin):

    raw_id_fields = ('project',)

    readonly_fields = ('amount', 'currency', 'fundraiser_name', 'mchanga_account',
                       'mpesa_id', 'mpesa_name', 'mpesa_phone',
                       'status', 'date', 'created', 'updated')

    list_display = ('date', 'amount', 'mpesa_name', 'project', 'fundraiser_name', 'mchanga_account')

    fields = ('project',) + readonly_fields

    export_fields = ['date', 'amount', 'project', 'mpesa_name', 'project', 'fundraiser_name', 'mchanga_account']
    actions = (export_as_csv_action(fields=export_fields), )


admin.site.register(MpesaPayment, MpesaAdmin)