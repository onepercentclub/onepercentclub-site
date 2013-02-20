from apps.bluebottle_drf2.serializers import SorlImageField
from django.contrib.auth.models import User
from rest_framework import serializers


class MemberDetailSerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='member-detail')
    picture = SorlImageField('userprofile.picture', '100x100', colorspace="GRAY")

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'url', 'picture')


class MemberListSerializer(MemberDetailSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'url')


class NoneHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """ Specialized version of HyperlinkedIdentityField that deals with None objects. """

    def field_to_native(self, obj, field_name):
        if obj is None:
            return ''
        else:
            super(NoneHyperlinkedIdentityField, self).field_to_native(obj, field_name)


class AuthenticatedMemberSerializer(MemberDetailSerializer):

    url = NoneHyperlinkedIdentityField(view_name='member-detail')

    class Meta(MemberDetailSerializer.Meta):
        fields = MemberDetailSerializer.Meta.fields + ('email', )
