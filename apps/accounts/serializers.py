from apps.accounts.models import UserProfile
from apps.bluebottle_drf2.serializers import SorlImageField, PostOnlyModelSerializer
from django.contrib.auth.models import User
from rest_framework import serializers


class UserPreviewSerializer(serializers.ModelSerializer):
    """
    Serializer for a subset of a member's public profile. This is usually embedded into other serializers.
    """
    avatar = SorlImageField('userprofile.picture', '90x90', crop='center', colorspace="GRAY")

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'avatar',)


class CurrentUserSerializer(UserPreviewSerializer):
    """
    Serializer for the current authenticated user. This is the same as the serializer for the member preview with the
    addition of id_for_ember.
    """
    # This is a hack to work around an issue with Ember-Data keeping the id as 'current'.
    id_for_ember = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = UserPreviewSerializer.Meta.fields + ('id_for_ember',)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for a member's public profile.
    """
    url = serializers.HyperlinkedIdentityField(view_name='user-profile-detail')
    username = serializers.CharField(required=False)
    avatar = SorlImageField('userprofile.picture', '100x100', colorspace="GRAY", required=False, read_only=True)
    picture = SorlImageField('userprofile.picture', '240x240', required=False)  # FIXME: read-only until we can write this field
    about = serializers.CharField(source='userprofile.about', required=False, read_only=True)  # FIXME: read-only until we can write this field
    why = serializers.CharField(source='userprofile.why', required=False, read_only=True)  # FIXME:read-only until we can write this field
    website = serializers.URLField(source='userprofile.website', required=False, read_only=True)  #  FIXME:read-only until we can write this field
    availability = serializers.ChoiceField(source='userprofile.availability', required=False, read_only=True)  # FIXME:read-only until we can write this field
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        # TODO: Add * Your skills,
        #           * interested in themes
        #           * interested in countries
        #           * interested in target groups
        fields = ('id', 'url', 'username', 'first_name', 'last_name', 'avatar', 'picture', 'about', 'why', 'website',
                  'availability', 'date_joined')


# TODO: Investigate if it's possible to integrate this into the UserProfileSerializer.
class UserCreateSerializer(UserProfileSerializer, PostOnlyModelSerializer):
    """
    Serializer for creating users. This is an extension if the UserProfileSerializer.
    """
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = UserPreviewSerializer.Meta.fields + ('email', 'password')
        postonly_fields = ('email', 'password')

    def process_postonly_fields(self, obj, post_attrs):
        # TODO: Add email confirmation on signup ... maybe use django-registration.
        obj.set_password(post_attrs['password'])
        obj.email = post_attrs['email']


class UserSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and editing a user's settings. This should only be accessible to authenticated users.
    """
    id = serializers.IntegerField(source='user.id', read_only=True)  # FIXME: This won't be required with a unified user model.
    email = serializers.EmailField(source='user.email', read_only=True)  # FIXME: read-only until we can write this field
    birthdate = serializers.DateTimeField(required=False)

    class Meta:
        model = UserProfile
        # TODO: Add * password update like it's done with the post only fields serializer (ie. create / add put only fields serializer)
        #           * Facebook connect
        #           * Address
        fields = ('id', 'email', 'newsletter', 'gender', 'birthdate')
