from apps.bluebottle_drf2.serializers import SorlImageField
from django.contrib.auth.models import User
from rest_framework import serializers


class MemberSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='member-detail')
    avatar = SorlImageField('userprofile.picture', '100x100', colorspace="GRAY")
    picture = SorlImageField('userprofile.picture', '240x240')

    about = serializers.CharField(source='userprofile.about')
    why = serializers.CharField(source='userprofile.why')
    contribution = serializers.CharField(source='userprofile.contribution')
    availability = serializers.CharField(source='userprofile.availability')
    working_location = serializers.CharField(source='userprofile.working_location')


    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'date_joined', 'url', 'picture', 'avatar', 'about', 'why',
                  'contribution', 'availability', 'working_location')


class NoneHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """ Specialized version of HyperlinkedIdentityField that deals with None objects. """

    def field_to_native(self, obj, field_name):
        if obj is None:
            return ''
        else:
            super(NoneHyperlinkedIdentityField, self).field_to_native(obj, field_name)


class AuthenticatedMemberSerializer(MemberSerializer):

    url = NoneHyperlinkedIdentityField(view_name='member-detail')

    class Meta(MemberSerializer.Meta):
        fields = MemberSerializer.Meta.fields + ('email', )
