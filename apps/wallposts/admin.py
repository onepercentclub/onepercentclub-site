from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from sorl.thumbnail.admin.compat import AdminImageMixin
from .models import WallPost, MediaWallPost, TextWallPost, MediaWallPostPhoto


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
