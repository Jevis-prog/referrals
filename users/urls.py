from django.urls import path

from . import views
from .views import ActivateInviteCodeView, ProfileView, RequestCodeView, VerifyCodeView

urlpatterns = [
    path('auth/request_code/', RequestCodeView.as_view(), name='request_code'),
    path('auth/verify_code/', VerifyCodeView.as_view(), name='verify_code'),
    path('profile_back/', ProfileView.as_view(), name='profile_back'),
    path('profile_back/activate_invite/', ActivateInviteCodeView.as_view(), name='activate_invite'),
    path('phone/', views.phone_view, name='phone'),
    path('code/', views.code_view, name='code'),
    path('profile/', views.profile_view, name='profile'),
]
