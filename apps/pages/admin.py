from apps.pages.models import Page, ContactMessage
from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import simplejson
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin
from fluent_contents.admin.placeholderfield import PlaceholderFieldAdmin
from fluent_contents.models import Placeholder
from fluent_contents.rendering import render_content_items, render_placeholder


class PageAdmin(PlaceholderFieldAdmin):
    list_display = ('title', 'slug', 'status_column', 'modification_date', 'language')
    list_filter = ('status', 'language', 'slug')
    date_hierarchy = 'publication_date'
    search_fields = ('slug', 'title')
    actions = ['make_published']
    model = Page
    ordering = ('language', 'slug', 'title')

    fieldsets = (
        (None, {
            'fields': ('title', 'body', 'language', 'slug'),
        }),
        (_('Publication settings'), {
            'fields': ('status', 'publication_date', 'publication_end_date'),
        }),
    )


    def preview_slide(self, obj):
        return obj.body

    prepopulated_fields = {'slug': ('title',),}

    radio_fields = {
        'status': admin.HORIZONTAL,
        'language': admin.HORIZONTAL,
    }

    def get_urls(self):
        # Include extra API views in this admin page
        base_urls = super(PageAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns = patterns('',
            url(r'^(?P<pk>\d+)/preview/$', self.admin_site.admin_view(self.preview_canvas), name="{0}_{1}_preview".format(*info)),
        )

        return urlpatterns + base_urls

    def get_base_object(self, pk):
        pk = long(pk)
        if pk:
            return Page.objects.get(pk=pk)
        else:
            return Page()

    @xframe_options_sameorigin
    def preview_canvas(self, request, pk):
        # Avoid the proxy model stuff, allow both to work.
        page = self.get_base_object(pk)
        return render(request, 'admin/pages/preview_canvas.html', {
            'page': page,
            'body': render_placeholder(request, page.body)
        })


    def _get_formset_objects(self, formset):
        all_objects = []
        def dummy_save_base(*args, **kwargs):
            pass

        # Based on BaseModelFormSet.save_existing_objects()
        # +  BaseModelFormSet.save_new_objects()
        for form in formset.initial_forms + formset.extra_forms:
            if formset.can_delete and formset._should_delete_form(form):
                continue

            if not form.is_valid():
                object = form.instance  # Keep old data
                # TODO: merge validated fields into object.
                # Before Django 1.5 that means manually constructing the values as form.cleaned_data is removed.
            else:
                object = form.save(commit=False)
                object.save_base = dummy_save_base  # Disable actual saving code.
                object.save()  # Trigger any pre-save code (e.g. fetch OEmbedItem, render CodeItem)

            all_objects.append(object)

        return all_objects

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        info = self.model._meta.app_label, self.model._meta.module_name
        context.update({
            'preview_canvas_url': reverse('admin:{0}_{1}_preview'.format(*info), kwargs={'pk': obj.pk if obj else 0}),
        })
        return super(PageAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        # Automatically store the user in the author field.
        if not change:
            obj.author = request.user

        if not obj.publication_date:
            # auto_now_add makes the field uneditable.
            # default fills the field before the post is written (too early)
            obj.publication_date = now()
        obj.save()

    STATUS_ICONS = {
        Page.PageStatus.published: 'icon-yes.gif',
        Page.PageStatus.draft: 'icon-unknown.gif',
    }

    def status_column(self, page):
        status = page.status
        title = [rec[1] for rec in page.PageStatus.choices if rec[0] == status].pop()
        icon  = self.STATUS_ICONS[status]
        admin = settings.STATIC_URL + 'admin/img/'
        return u'<img src="{admin}{icon}" width="10" height="10" alt="{title}" title="{title}" />'.format(admin=admin, icon=icon, title=title)

    status_column.allow_tags = True
    status_column.short_description = _('Status')


    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=Page.PageStatus.published)

        if rows_updated == 1:
            message = "1 entry was marked as published."
        else:
            message = "{0} entries were marked as published.".format(rows_updated)
        self.message_user(request, message)


    make_published.short_description = _("Mark selected entries as published")



admin.site.register(Page, PageAdmin)


class ContactMessageAdmin(admin.ModelAdmin):

    model = ContactMessage
    list_display = ('message', 'name', 'email', 'creation_date', 'status')
    list_filter = ('status', )
    search_fields = ('message', 'name', 'email')
    raw_id_fields = ('author', )

admin.site.register(ContactMessage, ContactMessageAdmin)