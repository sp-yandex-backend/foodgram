from rest_framework import serializers

from users.models import User

from api.models import Subscribe


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        id = self.instance.id
        following = User.objects.get(pk=id)
        return Subscribe.objects.filter(
            user=user, following=following
        ).exists()
