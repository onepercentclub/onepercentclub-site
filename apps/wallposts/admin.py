from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from .models import WallPost, MediaWallPost, TextWallPost


class MediaWallPostAdmin(PolymorphicChildModelAdmin):
    base_model = WallPost


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