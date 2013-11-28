from django.contrib import admin
from django.core.urlresolvers import reverse


from .models import Organization, OrganizationDocument, OrganizationMember
from .forms import OrganizationDocumentForm


class OrganizationDocumentInline(admin.StackedInline):
    model = OrganizationDocument
    form = OrganizationDocumentForm
    extra = 0
    raw_id_fields = ('author', )
    readonly_fields = ('download_url',)
    fields = readonly_fields + ('file', 'author')

    def download_url(self, obj):
        return "<a href='%s'>%s</a>" % (str(obj.document_url), 'Download')
    download_url.allow_tags = True


class OrganizationMemberInline(admin.StackedInline):
    model = OrganizationMember
    raw_id_fields = ('user', )
    extra = 0
    
class OrganizationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    exclude = ('registration',)

    inlines = (OrganizationMemberInline, OrganizationDocumentInline)

    search_fields = ('name', 'description')

admin.site.register(Organization, OrganizationAdmin)


class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'function', 'organization')
    list_filter = ('function',)
    raw_id_fields = ('user', )
    search_fields = ('user__first_name', 'user__last_name',
                     'user__username', 'organization__name')

admin.site.register(OrganizationMember, OrganizationMemberAdmin)
