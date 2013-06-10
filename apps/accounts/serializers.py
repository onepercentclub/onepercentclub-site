from apps.accounts.models import BlueBottleUser
from apps.bluebottle_drf2.serializers import SorlImageField
from django import forms
from django.contrib.sites.models import Site
from registration.models import RegistrationProfile
from rest_framework import serializers


class UserPreviewSerializer(serializers.ModelSerializer):
    """
    Serializer for a subset of a member's public profile. This is usually embedded into other serializers.
    """
    avatar = SorlImageField('picture', '90x90', crop='center', colorspace="GRAY")

    class Meta:
        model = BlueBottleUser
        fields = ('id', 'first_name', 'last_name', 'username', 'avatar',)


class CurrentUserSerializer(UserPreviewSerializer):
    """
    Serializer for the current authenticated user. This is the same as the serializer for the member preview with the
    addition of id_for_ember.
    """
    # This is a hack to work around an issue with Ember-Data keeping the id as 'current'.
    id_for_ember = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = BlueBottleUser
        fields = UserPreviewSerializer.Meta.fields + ('id_for_ember',)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for a member's public profile.
    """
    url = serializers.HyperlinkedIdentityField(view_name='user-profile-detail')
    avatar = SorlImageField('picture', '100x100', colorspace="GRAY", required=False, read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = BlueBottleUser
        # TODO: Add * Your skills,
        #           * interested in themes
        #           * interested in countries
        #           * interested in target groups
        fields = ('id', 'url', 'username', 'first_name', 'last_name', 'avatar', 'picture', 'about', 'why', 'website',
                  'availability', 'date_joined', 'location')


# Thanks to Neamar Tucote for this code:
# https://groups.google.com/d/msg/django-rest-framework/abMsDCYbBRg/d2orqUUdTqsJ
class PasswordField(serializers.CharField):
    """ Special field to update a password field. """
    widget = forms.widgets.PasswordInput
    hidden_password_string = '********'

    def from_native(self, value):
        """ Hash if new value sent, else retrieve current password. """
        from django.contrib.auth.hashers import make_password
        if value == self.hidden_password_string or value == '':
            return self.parent.object.password
        else:
            return make_password(value)

    def to_native(self, value):
        """ Hide hashed-password in API display. """
        return self.hidden_password_string


class UserSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and editing a user's settings. This should only be accessible to authenticated users.
    """
    # FIXME: We should really be serializing 'birthdate' as a DateField but that would require some additional work
    #        in our ember-data adapter. This could cause birthdate's to not be savable in some cases.
    birthdate = serializers.DateTimeField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = BlueBottleUser
        # TODO: Add * password update like it's done with the post only fields serializer (ie. create / add put only fields serializer)
        #           * Facebook connect
        #           * Address
        fields = ('id', 'email', 'share_time_knowledge', 'share_time_knowledge', 'newsletter', 'gender', 'birthdate', 'user_type')


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating users. This can only be used for creating users (POST) and should not be used for listing,
    editing or viewing users.
    """
    email = serializers.EmailField(required=True, max_length=254)
    password = PasswordField(required=True, max_length=128)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = BlueBottleUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password')

    def save(self):
        """
        Setup the newly created user for activation. We're not using
        'RegistrationProfile.objects.create_inactive_user()' from django-registration because it requires a username.
        """
        # Ensure User is inactive
        self.object.is_active = False
        self.object.save()

        # Create a RegistrationProfile and email its activation key to the User.
        registration_profile = RegistrationProfile.objects.create_profile(self.object)
        site = Site.objects.get_current()
        registration_profile.send_activation_email(site)
