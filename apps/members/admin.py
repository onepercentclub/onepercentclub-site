from django.contrib import admin

from bluebottle.bb_accounts.admin import BlueBottleUserAdmin

from .models import Member

class MemberAdmin(BlueBottleUserAdmin):
    pass



admin.site.register(Member, BlueBottleUserAdmin)