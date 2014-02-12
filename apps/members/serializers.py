from bluebottle.bb_accounts.serializers import (
    UserProfileSerializer as BaseUserProfileSerializer)

class UserProfileSerializer(BaseUserProfileSerializer):

    class Meta:
        model = BaseUserProfileSerializer.Meta.model
        fields = BaseUserProfileSerializer.Meta.fields + ()