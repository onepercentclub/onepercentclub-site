from django.core import urlresolvers
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import Language, UserAddress, UserProfile


class UserAddressAdmin(admin.StackedInline):
    model = UserAddress
    extra = 1


class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,
            {'fields': ['user_link', 'tags']}
            ),
        ("Settings",
             {'fields': ['interface_language', 'newsletter']}
            ),
        ("Basic Profile Information",
             {'fields': ['birthdate', 'gender', 'location', 'website',
                         'picture', 'languages', 'deleted']}
            ),
        ("In-depth Profile Information",
             {'fields': ['about', 'why', 'contribution',
                         'availability', 'working_location']}
            ),
    ]

    inlines = (UserAddressAdmin,)
    filter_horizontal = ('languages',)
    readonly_fields = ('user_link',)

    # http://stackoverflow.com/questions/5330598/making-django-readonly-foreignkey-field-in-admin-render-as-a-link
    def user_link(self, obj):
        change_url = urlresolvers.reverse('admin:auth_user_change', args=(obj.user.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.user.username))
    user_link.short_description = _("User")

admin.site.register(UserProfile, UserProfileAdmin)


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('user_profile_link',)}),)
    readonly_fields = ('user_profile_link',)

    # http://stackoverflow.com/questions/5330598/making-django-readonly-foreignkey-field-in-admin-render-as-a-link
    def user_profile_link(self, obj):
        profile = obj.get_profile()
        change_url = urlresolvers.reverse('admin:accounts_userprofile_change', args=(profile.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.username))
    user_profile_link.short_description = _("User Profile")

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Hopefully this model will be pre-populated with data and we won't need an
# Admin page for it.
admin.site.register(Language)