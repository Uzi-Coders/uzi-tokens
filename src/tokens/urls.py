from django.urls import path
from . import views

app_name = 'tokens'

urlpatterns = [
    path('', views.ApiTokenListCreateView.as_view(), name='api_tokens'),
    path('<int:token_id>/', views.ApiTokenDeleteView.as_view(), name='api_token_detail'),
    path('<int:token_id>/reveal/', views.ApiTokenRevealView.as_view(), name='api_token_reveal')
]