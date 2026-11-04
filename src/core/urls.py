from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path("csrf/", views.GetCSRFTokenAPIView.as_view(), name="csrf_token"),
    path("set-language/", views.SetLanguageAPIView.as_view(), name="set_language"),
]
