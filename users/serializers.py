from rest_framework import serializers  # type: ignore

from .models import User


class RequestCodeSerializer(serializers.Serializer):  # type: ignore
    phone_number: str = serializers.CharField(max_length=15)


class VerifyCodeSerializer(serializers.Serializer):  # type: ignore
    phone_number: str = serializers.CharField(max_length=15)
    code: str = serializers.CharField(max_length=4)


class ProfileSerializer(serializers.ModelSerializer):  # type: ignore
    invited_by_code = serializers.SerializerMethodField()
    invited_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['phone_number', 'invite_code', 'invited_by_code', 'invited_users']

    def get_invited_by_code(self, obj: User) -> str | None:
        return obj.invited_by.invite_code if obj.invited_by else None

    def get_invited_users(self, obj: User) -> list[str]:
        return [user.phone_number for user in obj.invited_users.all()]


class ActivateInviteCodeSerializer(serializers.Serializer):  # type: ignore
    invite_code: str = serializers.CharField(max_length=6)
