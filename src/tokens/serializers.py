from rest_framework import serializers

from .models import ApiToken


class ApiTokenCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64)
    permission = serializers.ChoiceField(
        choices=ApiToken.Permission.choices,
        default=ApiToken.Permission.READ,
    )


class ApiTokenSerializer(serializers.ModelSerializer):
    masked_token = serializers.ReadOnlyField()

    class Meta:
        model = ApiToken
        fields = ('id', 'name', 'masked_token', 'permission', 'created_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('reveal_full_key'):
            data['token'] = instance.token
        return data
