from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('register/<str:referral_code>/', views.register_user, name='register_with_referral'),  # Add this line
    path('login/', views.login_user, name='signin'),
    path('logout/', views.logout_user, name='signout'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_password/', views.update_password, name='update_password'),
    path('update_info/', views.update_info, name='update_info'),
    path('shipping_info/', views.shipping_info, name='shipping_info'),

    # Password Reset URLs
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
