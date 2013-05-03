from apps.accounts.models import UserProfile
from apps.bluebottle_drf2.serializers import SorlImageField
from django.contrib.auth.models import User
from rest_framework import serializers


class MemberSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='member-profile-detail')
    avatar = SorlImageField('userprofile.picture', '100x100', colorspace="GRAY")
    picture = SorlImageField('userprofile.picture', '240x240')

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'url', 'picture', 'avatar')


class AuthenticatedUserSerializer(MemberSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'url', 'picture', 'avatar', 'email')


class MemberProfileSerializer(MemberSerializer):
    about = serializers.CharField(source='userprofile.about', required=False)
    why = serializers.CharField(source='userprofile.why', required=False, read_only=False)
    contribution = serializers.CharField(source='userprofile.contribution', required=False)
    availability = serializers.CharField(source='userprofile.availability', required=False)
    working_location = serializers.CharField(source='userprofile.working_location', required=False)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'url', 'picture', 'avatar', 'about', 'why',
                  'contribution', 'availability', 'working_location')


class MemberSettingsSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='member-profile-detail')
    picture = serializers.ImageField(source='picture', required=False)

    username = serializers.CharField(source='user.username', read_only=True)

    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)


    email = serializers.EmailField(source='user.email', required=False)

    about = serializers.CharField(source='about', required=False, read_only=False)
    why = serializers.CharField(source='why', required=False, read_only=False)
    contribution = serializers.CharField(source='contribution', required=False)
    availability = serializers.CharField(source='availability', required=False)
    working_location = serializers.CharField(source='working_location', required=False)

    class Meta:
        model = UserProfile
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'url', 'picture', 'about', 'why',
                  'contribution', 'availability', 'working_location', 'about')


class NoneHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """ Specialized version of HyperlinkedIdentityField that deals with None objects. """

    def field_to_native(self, obj, field_name):
        if obj is None:
            return ''
        else:
            super(NoneHyperlinkedIdentityField, self).field_to_native(obj, field_name)
