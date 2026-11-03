import secrets
import string

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = get_user_model()


class ApiToken(models.Model):
    class Permission(models.TextChoices):
        READ = 'read', _("Read only")
        READ_WRITE = 'read_write', _("Read & write")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_tokens', verbose_name=_("User"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    token = models.CharField(max_length=64, unique=True, verbose_name=_("Token"))
    permission = models.CharField(max_length=16, choices=Permission.choices, default=Permission.READ,
                                  verbose_name=_("Permission"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Last used at"))

    class Meta:
        verbose_name = _("API Token")
        verbose_name_plural = _("API Tokens")

    @staticmethod
    def generate_key():
        alphabet = string.ascii_letters + string.digits
        return settings.API_TOKEN_PREFIX + "".join(
            secrets.choice(alphabet) for _i in range(settings.API_RANDOM_TOKEN_LENGTH)
        )

    @property
    def masked_token(self):
        return f"{self.token[:8]}{'*' * 16}{self.token[-4:]}"

    @property
    def can_write(self):
        return self.permission == self.Permission.READ_WRITE
