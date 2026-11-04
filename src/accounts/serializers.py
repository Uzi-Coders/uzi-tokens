from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def get_first_name(self, obj):
        return obj.first_name or None

    def get_last_name(self, obj):
        return obj.last_name or None

    def get_email(self, obj):
        return obj.email or None


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    first_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=150,
    )
    last_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=150,
    )
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')

    def validate(self, attrs):
        for field in ('first_name', 'last_name', 'email'):
            if attrs.get(field) is None:
                attrs[field] = ''

        user = User(username=attrs['username'])
        try:
            validate_password(attrs['password'], user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['username'],
            password=attrs['password'],
        )
        if user is None:
            raise serializers.ValidationError(_("Invalid username or password."))

        attrs['user'] = user
        return attrs
