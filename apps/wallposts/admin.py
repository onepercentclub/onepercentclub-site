from bluebottle.bluebottle_utils.utils import set_author_editor_ip
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.wallposts.models import SystemWallPost
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from sorl.thumbnail.admin.compat import AdminImageMixin
from .models import WallPost, MediaWallPost, TextWallPost, MediaWallPostPhoto, Reaction


class MediaWallPostPhotoInline(AdminImageMixin, admin.StackedInline):
    model = MediaWallPostPhoto
    extra = 0
    raw_id_fields = ('author', 'editor')


class MediaWallPostAdmin(PolymorphicChildModelAdmin):
    base_model = WallPost
    raw_id_fields = ('author', 'editor')
    list_display = ('created', 'view_project_online', 'get_text', 'video_url', 'photos', 'author')
    ordering = ('-created', )
    inlines = (MediaWallPostPhotoInline,)

    def get_text(self, obj):
        if len(obj.text) > 150:
            return u'<span title="{text}">{short_text} [...]</span>'.format(text=obj.text, short_text=obj.text[:145])
    get_text.allow_tags = True

    def photos(self, obj):
        photos = MediaWallPostPhoto.objects.filter(mediawallpost=obj)
        if len(photos):
            return len(photos)
        return '-'

    def view_project_online(self, obj):
        return u'<a href="/go/projects/{slug}">{title}</a>'.format(slug=obj.content_object.slug, title=obj.content_object.title)
    view_project_online.allow_tags = True



class TextWallPostAdmin(PolymorphicChildModelAdmin):
    base_model = WallPost
    list_display = ('created', 'author', 'content_type', 'text')
    raw_id_fields = ('author', 'editor')
    ordering =  ('-created', )


class SystemWallPostAdmin(PolymorphicChildModelAdmin):
    base_model = WallPost
    list_display = ('created', 'author', 'content_type', 'related_type', 'text')
    raw_id_fields = ('author', 'editor')
    ordering = ('-created', )


class WallPostParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = WallPost
    list_display = ('created', 'author', 'content_type')
    ordering = ('-created', )
    child_models = (
        (MediaWallPost, MediaWallPostAdmin),
        (TextWallPost, TextWallPostAdmin),
        (SystemWallPost, SystemWallPostAdmin),
    )

# Only the parent needs to be registered:
admin.site.register(WallPost, WallPostParentAdmin)

admin.site.register(MediaWallPost, MediaWallPostAdmin)
admin.site.register(TextWallPost, TextWallPostAdmin)
admin.site.register(SystemWallPost, SystemWallPostAdmin)


class ReactionAdmin(admin.ModelAdmin):
    # created and updated are auto-set fields. author, editor and ip_address are auto-set on save.
    readonly_fields = ('created', 'updated', 'author', 'editor', 'ip_address')
    list_display = ('author_full_name', 'created', 'updated', 'deleted', 'ip_address')
    list_filter = ('created', 'updated', 'deleted')
    date_hierarchy = 'created'
    ordering = ('-created',)
    raw_id_fields = ('author', 'editor')
    search_fields = ('text', 'author__username', 'author__email', 'author__first_name', 'author__last_name', 'ip_address')

    def get_fieldsets(self, request, obj=None):
        """ Only show the relevant fields when adding a Reaction. """
        if obj: # editing an existing object
            return super(ReactionAdmin, self).get_fieldsets(request, obj)
        return [(None, {'fields': ('wallpost', 'text')})]

    def author_full_name(self, obj):
        full_name = obj.author.get_full_name()
        if not full_name:
            return obj.author.username
        else:
            return full_name

    author_full_name.short_description = _('Author')

    def save_model(self, request, obj, form, change):
        """ Set the author or editor (as required) and ip when saving the model. """
        set_author_editor_ip(request, obj)
        super(ReactionAdmin, self).save_model(request, obj, form, change)

    def queryset(self, request):
        """ The Admin needs to show all the Reactions. """
        return Reaction.objects_with_deleted.all()

admin.site.register(Reaction, ReactionAdmin)
