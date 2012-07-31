from django.contrib import admin

from apps.organizations.models import (
    Organization, OrganizationAddress, OrganizationMember
)


class OrganizationAddressAdmin(admin.StackedInline):
    model = OrganizationAddress
    extra = 1


class OrganizationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

    inlines = (OrganizationAddressAdmin,)

    search_fields = ('title', 'description')


admin.site.register(Organization, OrganizationAdmin)

admin.site.register(OrganizationMember)
