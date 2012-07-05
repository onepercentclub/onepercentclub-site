from apps.organizations.models import Organization, OrganizationAddress
from django.contrib import admin


class OrganizationAddressAdmin(admin.StackedInline):
    model = OrganizationAddress
    extra = 1


class OrganizationAdmin(admin.ModelAdmin):
    inlines = (OrganizationAddressAdmin,)


admin.site.register(Organization, OrganizationAdmin)
