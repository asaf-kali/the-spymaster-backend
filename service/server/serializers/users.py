from rest_framework import serializers

from server.models.user import SpymasterUser


class UserSummarizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpymasterUser
        fields = ["id", "username", "first_name", "last_name", "full_name"]


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpymasterUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "is_staff",
            "is_superuser",
        ]
