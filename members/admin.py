from django.contrib import admin

from .models import Member


class MemberAdmin(admin.ModelAdmin):
    pass
admin.site.register(Member, MemberAdmin)