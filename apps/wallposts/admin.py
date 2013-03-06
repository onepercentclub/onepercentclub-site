from apps.bluebottle_utils.utils import set_author_editor_ip
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from sorl.thumbnail.admin.compat import AdminImageMixin
from .models import WallPost, MediaWallPost, TextWallPost, MediaWallPostPhoto, Reaction


class MediaWallPostPhotoInline(AdminImageMixin, admin.StackedInline):
    model = MediaWallPostPhoto
    extra = 0


class MediaWallPostAdmin(PolymorphicChildModelAdmin):
    base_model = WallPost
    inlines = (MediaWallPostPhotoInline,)


class TextWallPostAdmin(PolymorphicChildModelAdmin):
    base_model = WallPost


class WallPostParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = WallPost
    child_models = (
        (MediaWallPost, MediaWallPostAdmin),
        (TextWallPost, TextWallPostAdmin),
    )

# Only the parent needs to be registered:
admin.site.register(WallPost, WallPostParentAdmin)


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