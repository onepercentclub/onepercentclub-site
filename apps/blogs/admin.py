from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from fluent_contents.admin.placeholderfield import PlaceholderFieldAdmin
from fluent_contents.models import Placeholder
from fluent_contents.rendering import render_placeholder
from apps.blogs.models import BlogPost, BlogPostProxy, NewsPostProxy


class BlogPostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlogPostForm, self).__init__(*args, **kwargs)
        self.fields['publication_date'].required = False  # The admin's .save() method fills in a default.


class BlogPostAdmin(PlaceholderFieldAdmin):
    list_display = ('title', 'status_column', 'modification_date')
    list_filter = ('status',)
    date_hierarchy = 'publication_date'
    search_fields = ('slug', 'title')
    actions = ['make_published']
    form = BlogPostForm

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'language', 'main_image', 'contents',),
        }),
        (_('Publication settings'), {
            'fields': ('status', 'publication_date', 'publication_end_date', 'allow_comments'),
        }),
        (_("Taxonomy"), {
            'fields': ('categories', 'tags', 'countries'),
        }),
    )

    prepopulated_fields = {'slug': ('title',),}
    radio_fields = {
        'status': admin.HORIZONTAL,
        'language': admin.HORIZONTAL,
    }


    def get_urls(self):
        # Include extra API views in this admin page
        base_urls = super(BlogPostAdmin, self).get_urls()
        urlpatterns = patterns('',
            url(r'^(?P<pk>\d+)/get_preview/$', self.admin_site.admin_view(self.get_preview_html), name="blogs_blogpost_get_preview")
        )

        return urlpatterns + base_urls


    def get_preview_html(self, request, pk):
        """
        Ajax view to return the preview.
        """
        pk = long(pk)
        if pk:
            blogpost = self.get_object(request, pk)
            placeholder = blogpost.contents
        else:
            blogpost = self.model()
            placeholder = Placeholder()

        # Get fluent-contents placeholder
        contents_html = render_placeholder(request, placeholder, parent_object=blogpost)

        status = 200
        json = {
            'success': True,
            'title': blogpost.title,
            'contents': contents_html,
        }
        return HttpResponse(simplejson.dumps(json), content_type='application/javascript', status=status)


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
        BlogPost.PostStatus.published: 'icon-yes.gif',
        BlogPost.PostStatus.draft: 'icon-unknown.gif',
    }


    def status_column(self, blogpost):
        status = blogpost.status
        title = [rec[1] for rec in blogpost.PostStatus.choices if rec[0] == status].pop()
        icon  = self.STATUS_ICONS[status]
        admin = settings.STATIC_URL + 'admin/img/'
        return u'<img src="{admin}{icon}" width="10" height="10" alt="{title}" title="{title}" />'.format(admin=admin, icon=icon, title=title)

    status_column.allow_tags = True
    status_column.short_description = _('Status')


    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=BlogPost.PostStatus.published)

        if rows_updated == 1:
            message = "1 entry was marked as published."
        else:
            message = "{0} entries were marked as published.".format(rows_updated)
        self.message_user(request, message)


    make_published.short_description = _("Mark selected entries as published")



admin.site.register(BlogPostProxy, BlogPostAdmin)
admin.site.register(NewsPostProxy, BlogPostAdmin)
