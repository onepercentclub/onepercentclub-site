from apps.accounts.models import BlueBottleUser
from apps.bluebottle_drf2.serializers import SorlImageField, PostOnlyModelSerializer
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

    class Meta:
        model = BlueBottleUser
        # TODO: Add * Your skills,
        #           * interested in themes
        #           * interested in countries
        #           * interested in target groups
        fields = ('id', 'url', 'first_name', 'last_name', 'avatar', 'picture', 'about', 'why', 'website',
                  'availability', 'date_joined')


# TODO: Investigate if it's possible to integrate this into the UserProfileSerializer.
class UserCreateSerializer(UserProfileSerializer, PostOnlyModelSerializer):
    """
    Serializer for creating users. This is an extension if the UserProfileSerializer.
    """
    email = serializers.EmailField(required=True)

    class Meta:
        model = BlueBottleUser
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
    email = serializers.EmailField(required=False)

    class Meta:
        model = BlueBottleUser
        # TODO: Add * password update like it's done with the post only fields serializer (ie. create / add put only fields serializer)
        #           * Facebook connect
        #           * Address
        fields = ('id', 'email', 'newsletter', 'gender', 'birthdate')
