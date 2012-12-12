from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from .models import WallPost, MediaWallPost, TextWallPost


class WallPostChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = WallPost


class MediaWallPostAdmin(WallPostChildAdmin):
    # define custom features here
    pass


class TextWallPostAdmin(WallPostChildAdmin):
    # define custom features here
    pass


class WallPostParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = WallPost
    child_models = (
        (MediaWallPost, MediaWallPostAdmin),
        (TextWallPost, TextWallPostAdmin),
    )

# Only the parent needs to be registered:
admin.site.register(WallPost, WallPostParentAdmin)