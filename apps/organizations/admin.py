from django.contrib import admin
from .models import Organization, OrganizationAddress, OrganizationMember


class OrganizationAddressInline(admin.StackedInline):
    model = OrganizationAddress
    extra = 0


class OrganizationMemberInline(admin.StackedInline):
    model = OrganizationMember
    raw_id_fields = ('user', )
    extra = 0


class OrganizationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

    inlines = (OrganizationAddressInline, OrganizationMemberInline)

    search_fields = ('name', 'description')

admin.site.register(Organization, OrganizationAdmin)


class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'function', 'organization')
    list_filter = ('function',)
    raw_id_fields = ('user', )
    search_fields = ('user__first_name', 'user__last_name',
                     'user__username', 'organization__name')

admin.site.register(OrganizationMember, OrganizationMemberAdmin)