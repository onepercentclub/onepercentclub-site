from django.contrib import admin

from apps.organizations.models import (
    Organization, OrganizationAddress, OrganizationMember
)


class OrganizationAddressAdmin(admin.StackedInline):
    model = OrganizationAddress
    extra = 0


class OrganizationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

    inlines = (OrganizationAddressAdmin,)

    search_fields = ('name', 'description')

admin.site.register(Organization, OrganizationAdmin)


class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'function', 'organization')
    list_filter = ('function',)
    search_fields = ('user__first_name', 'user__last_name',
                     'user__username', 'organization__name')

admin.site.register(OrganizationMember, OrganizationMemberAdmin)