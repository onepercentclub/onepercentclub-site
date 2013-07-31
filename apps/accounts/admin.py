from apps.accounts.models import BlueBottleUser
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import UserAddress


class UserAddressAdmin(admin.StackedInline):
    model = UserAddress
    extra = 0


class BlueBottleUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given email and password.
    """
    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    email = forms.EmailField(label=_("email address"), max_length=254,
                             help_text=_("Required. 254 characters or fewer. A valid email address."))
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = BlueBottleUser
        fields = ("email",)

    def clean_email(self):
        # Since BlueBottleUser.email is unique, this check is redundant but it sets a nicer error message than the ORM.
        email = self.cleaned_data["email"]
        try:
            BlueBottleUser._default_manager.get(email=email)
        except BlueBottleUser.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(BlueBottleUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class BlueBottleUserChangeForm(forms.ModelForm):
    email = forms.EmailField(label=_("email address"), max_length=254,
                             help_text=_("Required. 254 characters or fewer. A valid email address."))
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = BlueBottleUser

    def __init__(self, *args, **kwargs):
        super(BlueBottleUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class BlueBottleAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'username', 'gender', 'birthdate', 'phone_number')}),
        (_("Profile"), {'fields': ('user_type', 'picture', 'about', 'why', 'availability', 'location', 'website')}),
        (_("Settings"), {'fields': ['primary_language', 'newsletter']}),
        (_("Data from old website"), {'fields': ('available_time', 'contribution', 'tags')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'deleted')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

    readonly_fields = ('date_joined', 'last_login', 'updated', 'deleted')

    # This post describes how you could put the address closer to the 'Personal Info' section.
    # https://groups.google.com/d/msg/django-users/yUq2Nvx_4eM/30_EkjePrOAJ
    inlines = (UserAddressAdmin,)

    form = BlueBottleUserChangeForm
    add_form = BlueBottleUserCreationForm

    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser')

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'is_active')
    ordering = ('-date_joined', 'email',)


admin.site.register(BlueBottleUser, BlueBottleAdmin)