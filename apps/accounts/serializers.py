from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import HyperlinkedIdentityField


class MemberDetailSerializer(serializers.ModelSerializer):

    url = HyperlinkedIdentityField(view_name='member-detail')

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'url')


class MemberListSerializer(MemberDetailSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'url')
