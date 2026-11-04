from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ApiToken


@admin.register(ApiToken)
class ApiTokenAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'permission', 'created_at', 'last_used_at',
    )
    list_filter = ('permission', 'is_active')
    search_fields = ('name', 'user__username')
    readonly_fields = ('token', 'masked_token_display', 'created_at', 'last_used_at')
    ordering = ('-created_at',)

    @admin.display(description=_("Masked token"))
    def masked_token_display(self, obj):
        return obj.masked_token if obj.token else '-'

    def save_model(self, request, obj, form, change):
        if not obj.token:
            for _attempt in range(5):
                candidate = ApiToken.generate_key()
                if not ApiToken.objects.filter(token=candidate).exists():
                    obj.token = candidate
                    break
            else:
                raise ValueError(_("Could not generate a unique API token."))
        super().save_model(request, obj, form, change)
